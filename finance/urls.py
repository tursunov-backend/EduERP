from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, PaymentViewSet, TeacherSalaryViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'teacher-salaries', TeacherSalaryViewSet, basename='teachersalary')

urlpatterns = [
    path('', include(router.urls)),
]