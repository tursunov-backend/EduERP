from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Student, StudentStatus


class StudentService:
    @staticmethod
    def freeze_student(student: Student) -> Student:
        if student.status == StudentStatus.FROZEN:
            raise ValidationError("Talaba allaqachon muzlatilgan.")

        student.status = StudentStatus.FROZEN
        student.frozen_at = timezone.now()
        student.save()
        return student

    @staticmethod
    def unfreeze_student(student: Student) -> Student:
        if student.status != StudentStatus.FROZEN:
            raise ValidationError("Talaba muzlatilgan holatda emas.")

        student.status = StudentStatus.ACTIVE
        student.frozen_at = None
        student.save()
        return student

    @staticmethod
    def archive_student(student: Student) -> Student:
        student.status = StudentStatus.ARCHIVED
        student.archived_at = timezone.now()
        student.save()
        return student

    @staticmethod
    @transaction.atomic
    def transfer_student(student: Student, current_group, target_group):
        if target_group.students.count() >= target_group.max_student:
            raise ValidationError(f"Guruh to'lgan! Maksimal sig'im: {target_group.max_student}")

        current_group.students.remove(student)
        target_group.students.add(student)
        return student