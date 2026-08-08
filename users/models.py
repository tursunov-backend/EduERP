from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]

    def __str__(self):
        return self.username