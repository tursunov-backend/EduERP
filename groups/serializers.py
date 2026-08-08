from rest_framework import serializers
from .models import Group

class GroupSerializer(serializers.ModelSerializer):
    students_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'date_start',
            'date_end',
            'price',
            'days',
            'time_start',
            'time_end',
            'status',
            'room',
            'max_student',
            'teacher',
            'students',
            'students_count',
        ]

class AssignTeacherSerializer(serializers.Serializer):
    teacher_id = serializers.UUIDField()

class AddStudentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()