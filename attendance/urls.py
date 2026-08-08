from django.urls import path

from .views import (
    AttendancesView,
    AttendanceView,
    AttendanceRecordsView,
    AttendanceMarkView,
    AttendanceRecordsListView,
    AttendanceRecordView,
)

urlpatterns = [
    path('attendances/', AttendancesView.as_view(), name='attendances'),
    path('attendances/<int:pk>/', AttendanceView.as_view(), name='attendance'),
    path('attendances/<int:pk>/records/', AttendanceRecordsView.as_view(), name='attendance-records'),
    path('attendances/<int:pk>/mark/', AttendanceMarkView.as_view(), name='attendance-mark'),

    path('attendance-records/', AttendanceRecordsListView.as_view(), name='attendance-records-list'),
    path('attendance-records/<int:pk>/', AttendanceRecordView.as_view(), name='attendance-record'),
]