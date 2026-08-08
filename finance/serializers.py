from rest_framework import serializers
from django.contrib.auth import get_user_model

from students.models import Student
from students.serializers import StudentSerializer
from .models import Category, Transaction, Payment, TeacherSalary

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'category', 'category_name', 
            'payment_method', 'date', 'description', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['id', 'date', 'created_by']


class PaymentSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    student_lastname = serializers.CharField(source='student.last_name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'student', 'student_name', 'student_lastname', 'transaction', 'month_for']


class PaymentCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Transaction.PAYMENT_METHODS, default='cash')
    month_for = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_student_id(self, value):
        if not Student.objects.filter(id=value).exists():
            raise serializers.ValidationError("Bunday IDga ega talaba topilmadi.")
        return value

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value, type='income').exists():
            raise serializers.ValidationError("Tanlangan kategoriya topilmadi yoki u 'Kirim' turiga tegishli emas.")
        return value


class TeacherSalarySerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    teacher_username = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = TeacherSalary
        fields = ['id', 'teacher', 'teacher_name', 'teacher_username', 'transaction', 'for_month']


class TeacherSalaryCreateSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Transaction.PAYMENT_METHODS, default='cash')
    for_month = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_teacher_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("Bunday IDga ega foydalanuvchi topilmadi.")
        if getattr(user, 'role', None) != 'teacher':
            raise serializers.ValidationError("Tanlangan foydalanuvchi o'qituvchi (teacher) rolida emas.")
        return value

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value, type='expense').exists():
            raise serializers.ValidationError("Tanlangan kategoriya topilmadi yoki u 'Chiqim' (expense) turiga tegishli emas.")
        return value