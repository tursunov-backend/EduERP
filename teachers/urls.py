from django.urls import path

from .views import (
    TeachersView,
    TeacherView,
    MyTeacherProfileView,
    SubjectsView,
    SubjectView,
    TeacherWorkloadsView,
    TeacherWorkloadView,
    TransactionsView,
    TransactionView,
    ContractsView,
    ContractView,
    HomeWorksView,
    HomeWorkView,
    StudentGamificationsView,
    StudentGamificationView,
    ExamsView,
    ExamView,
    ExamResultsView,
    ExamResultView,
)

urlpatterns = [
    path('teachers/', TeachersView.as_view(), name='teachers'),
    path('teachers/me/', MyTeacherProfileView.as_view(), name='my-teacher-profile'),
    path('teachers/<int:pk>/', TeacherView.as_view(), name='teacher'),

    path('subjects/', SubjectsView.as_view(), name='subjects'),
    path('subjects/<int:pk>/', SubjectView.as_view(), name='subject'),

    path('workloads/', TeacherWorkloadsView.as_view(), name='workloads'),
    path('workloads/<int:pk>/', TeacherWorkloadView.as_view(), name='workload'),

    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('transactions/<int:pk>/', TransactionView.as_view(), name='transaction'),

    path('contracts/', ContractsView.as_view(), name='contracts'),
    path('contracts/<int:pk>/', ContractView.as_view(), name='contract'),

    path('homeworks/', HomeWorksView.as_view(), name='homeworks'),
    path('homeworks/<uuid:pk>/', HomeWorkView.as_view(), name='homework'),

    path('gamification/', StudentGamificationsView.as_view(), name='gamifications'),
    path('gamification/<uuid:pk>/', StudentGamificationView.as_view(), name='gamification'),

    path('exams/', ExamsView.as_view(), name='exams'),
    path('exams/<uuid:pk>/', ExamView.as_view(), name='exam'),

    path('exam-results/', ExamResultsView.as_view(), name='exam-results'),
    path('exam-results/<uuid:pk>/', ExamResultView.as_view(), name='exam-result'),
]