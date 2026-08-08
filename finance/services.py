from django.db import transaction

from .models import Transaction, Payment, Category, TeacherSalary


def process_student_payment(student, amount, category_id, payment_method, month_for, created_by, description=""):
    with transaction.atomic():
        category = Category.objects.get(id=category_id, type='income')
        
        txn = Transaction.objects.create(
            title=f"To'lov: {student}",
            amount=amount,
            category=category,
            payment_method=payment_method,
            description=description,
            created_by=created_by
        )
        
        payment = Payment.objects.create(
            student=student,
            transaction=txn,
            month_for=month_for
        )
        
        return payment


def process_teacher_salary(teacher, amount, category_id, payment_method, for_month, created_by, description=""):
    with transaction.atomic():
        category = Category.objects.get(id=category_id, type='expense')
        
        txn = Transaction.objects.create(
            title=f"Oylik: {teacher.get_full_name() or teacher.username}",
            amount=amount,
            category=category,
            payment_method=payment_method,
            description=description,
            created_by=created_by
        )
        
        salary = TeacherSalary.objects.create(
            teacher=teacher,
            transaction=txn,
            for_month=for_month
        )
        
        return salary