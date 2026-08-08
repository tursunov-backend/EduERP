from rest_framework import serializers
from .models import (
    Teacher,
    Subject,
    TeacherWorkload,
    Transaction,
    Contract,
    HomeWork,
    StudentGamification,
    Exam,
    ExamResult,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class TeacherSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subjects",
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Teacher
        fields = [
            "id",
            "first_name",
            "last_name",
            "bio",
            "owner",
            "subjects",
            "subject_ids",
            "amount",
            "salary_type",
        ]
        read_only_fields = ["owner"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        is_owner = bool(user and user.is_authenticated and instance.owner_id == user.id)
        is_staff = bool(user and user.is_staff)
        if not (is_owner or is_staff):
            data.pop("amount", None)
            data.pop("salary_type", None)
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        is_staff = bool(request and request.user and request.user.is_staff)
        if not is_staff:
            validated_data.pop("amount", None)
            validated_data.pop("salary_type", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        is_staff = bool(request and request.user and request.user.is_staff)
        if not is_staff:
            validated_data.pop("amount", None)
            validated_data.pop("salary_type", None)
        return super().update(instance, validated_data)


class TeacherWorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherWorkload
        fields = ["id", "teacher", "group", "hours_per_week", "created_at"]
        read_only_fields = ["created_at"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "teacher", "transaction_type", "comment", "amount", "date_added"]
        read_only_fields = ["date_added"]


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ["id", "teacher", "number", "start_date", "end_date", "file", "is_active", "created_at"]
        read_only_fields = ["created_at"]


class HomeWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeWork
        fields = [
            "id",
            "lesson",
            "description",
            "max_score",
            "status",
            "due_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentGamificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGamification
        fields = ["id", "student", "xp", "level"]
        read_only_fields = ["id"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "id",
            "lesson",
            "title",
            "description",
            "max_score",
            "status",
            "exam_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ["id", "exam", "student", "score", "graded_at"]
        read_only_fields = ["id", "graded_at"]

    def validate(self, attrs):
        exam = attrs.get("exam") or getattr(self.instance, "exam", None)
        score = attrs.get("score")
        if exam is not None and score is not None and score > exam.max_score:
            raise serializers.ValidationError(
                {"score": "Ball imtihonning maksimal balidan oshmasligi kerak."}
            )
        return attrs