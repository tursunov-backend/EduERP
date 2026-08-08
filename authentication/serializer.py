from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = str(user.id)
        token["username"] = user.username

        if hasattr(user, "role"):
            token["role"] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "role": getattr(self.user, "role", None),
        }

        return data


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
        )
        read_only_fields = fields


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            raise serializers.ValidationError("Invalid or expired refresh token.")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
            )

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from old password."}
            )

        validate_password(attrs["new_password"], user)

        return attrs

    def save(self):
        user = self.context["request"].user

        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])

        # Blacklist all refresh tokens
        outstanding_tokens = OutstandingToken.objects.filter(user=user)

        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }



class BaseCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    role = None

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            role=self.role,
        )


class CreateAdminSerializer(BaseCreateUserSerializer):
    role = "admin"


class CreateTeacherSerializer(BaseCreateUserSerializer):
    role = "teacher"


class CreateStudentSerializer(BaseCreateUserSerializer):
    role = "student"