from django.db import models
from django.conf import settings

from students.models import Student


class Category(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Kirim'),
        ('expense', 'Chiqim'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Naqd'),
        ('card', 'Karta / P2P'),
        ('bank', 'Bank o\'tkazmasi'),
        ('click_payme', 'Click / Payme'),
    )

    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount} UZS"


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='payment_details')
    month_for = models.DateField(help_text="Qaysi oy uchun to'lov qilingani (masalan: 2026-08-01)")

    def __str__(self):
        return f"{self.student} - {self.transaction.amount} UZS"


class TeacherSalary(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='salaries',
        limit_choices_to={'role': 'teacher'}
    )
    transaction = models.OneToOneField(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='salary_details'
    )
    for_month = models.DateField(help_text="Qaysi oy uchun oylik berilayotgani (masalan: 2026-08-01)")

    def __str__(self):
        return f"{self.teacher.get_full_name() or self.teacher.username} - {self.transaction.amount} UZS ({self.for_month})"