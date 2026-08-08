import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class StudentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    FROZEN = 'FROZEN', 'Frozen'
    ARCHIVED = 'ARCHIVED', 'Archived'


phone_validator = RegexValidator(regex=r'^\+998\d{9}$', message="Format: +998901234567")


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_regax = models.CharField(validators=[phone_validator], max_length=13, blank=True, null=True)
    passport_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(validators=[phone_validator], max_length=13, unique=True)
    # groups = models.ManyToManyField('Group', related_name='students', blank=True)
    status = models.CharField(
        max_length=20, 
        choices=StudentStatus.choices, 
        default=StudentStatus.ACTIVE
    )
    balance = models.BigIntegerField(default=0)
    frozen_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"