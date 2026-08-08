from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin, IsTeacher, IsStudent 
from .models import Transaction, Payment, TeacherSalary
from .serializers import TransactionSerializer, PaymentSerializer, TeacherSalarySerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'student':
            return Payment.objects.filter(student__user=user).order_by('-transaction__date')
        
        return Payment.objects.all().order_by('-transaction__date')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, (IsAdmin | IsStudent)]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]
            
        return [permission() for permission in permission_classes]


class TeacherSalaryViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSalarySerializer

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'teacher':
            return TeacherSalary.objects.filter(teacher__user=user).order_by('-transaction__date')
        
        return TeacherSalary.objects.all().order_by('-transaction__date')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, (IsAdmin | IsTeacher)]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]
            
        return [permission() for permission in permission_classes]