from rest_framework import serializers

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'owner', 'first_name', 'last_name',
            'phone_number', 'passport_number', 'status', 'balance',
            'frozen_at', 'archived_at',
        ]
        read_only_fields = ['status', 'balance', 'frozen_at', 'archived_at']


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['owner', 'first_name', 'last_name', 'phone_number', 'passport_number', 'groups']


class TransferStudentSerializer(serializers.Serializer):
    current_group_id = serializers.IntegerField()
    target_group_id = serializers.IntegerField()