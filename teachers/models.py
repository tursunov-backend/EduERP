import uuid

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth import get_user_model

from groups.models import Group
from students.models import Student

User = get_user_model()

CONTRACT_FILE_MAX_SIZE_MB = 15  
CONTRACT_ALLOWED_EXTENSIONS = ["pdf", "doc", "docx"]


def validate_contract_file_size(file):
    max_bytes = CONTRACT_FILE_MAX_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(
            f"Fayl hajmi {CONTRACT_FILE_MAX_SIZE_MB}MB dan oshmasligi kerak."
        )


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher"
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="teachers",
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    class SalaryType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        BIWEEKLY = "biweekly", "Biweekly (2 marta oyiga)"
        PER_LESSON = "per_lesson", "Per Lesson"

    salary_type = models.CharField(
        max_length=20,
        choices=SalaryType.choices,
        default=SalaryType.MONTHLY
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TeacherWorkload(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="workloads"
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="workloads"
    )
    hours_per_week = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("teacher", "group")

    def __str__(self):
        return f"{self.teacher} - {self.group} ({self.hours_per_week} soat/hafta)"


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        SALARY = "salary", "Salary"
        BONUS = "bonus", "Bonus"
        PENALTY = "penalty", "Penalty"
        OTHER = "other", "Other"

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    comment = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher} - {self.transaction_type} - {self.amount}"


class Contract(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="contracts"
    )
    number = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    file = models.FileField(
        upload_to="contracts/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=CONTRACT_ALLOWED_EXTENSIONS),
            validate_contract_file_size,
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shartnoma #{self.number} - {self.teacher}"

class HomeWork(models.Model):

    class Status(models.IntegerChoices):
        DRAFT = 0, "Draft"
        PUBLISHED = 1, "Published"
        CLOSED = 2, "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # lesson = models.ForeignKey(
    #     Lessons,
    #     on_delete=models.CASCADE,
    #     related_name="homeworks"
    # )
    description = models.TextField()
    max_score = models.PositiveIntegerField()
    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Uy vazifa - {self.lesson} (due {self.due_date:%Y-%m-%d})"


class Exam(models.Model):

    class Status(models.IntegerChoices):
        DRAFT = 0, "Draft"
        PUBLISHED = 1, "Published"
        CLOSED = 2, "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # lesson = models.ForeignKey(
    #     Lessons,
    #     on_delete=models.CASCADE,
    #     related_name="exams"
    # )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField()
    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT)
    exam_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imtihon - {self.title} ({self.lesson})"


class ExamResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="exam_results"
    )
    score = models.PositiveIntegerField()
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "student"],
                name="unique_examresult_exam_student",
            )
        ]

    def clean(self):
        if self.score is not None and self.exam_id and self.score > self.exam.max_score:
            raise ValidationError(
                {"score": "Ball imtihonning maksimal balidan oshmasligi kerak."}
            )

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.score}"


class StudentGamification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="gamification"
    )
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student} - level {self.level} ({self.xp} XP)"