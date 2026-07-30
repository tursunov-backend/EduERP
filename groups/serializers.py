from rest_framework import serializers
from .models import Group, GroupStudent

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class AssignTeacherSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()

class AddStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()