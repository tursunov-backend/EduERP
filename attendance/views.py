from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Attendance, AttendanceRecord
from .serializers import (
    AttendanceSerializer,
    AttendanceCreateSerializer,
    AttendanceRecordSerializer,
)
from .permissions import IsGroupTeacher
from teachers.models import Teacher


class AttendancesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AttendanceCreateSerializer
        return AttendanceSerializer

    def get_queryset(self):
        qs = Attendance.objects.all().order_by("-date")
        if not self.request.user.is_staff:
            teacher = get_object_or_404(Teacher, owner=self.request.user)
            qs = qs.filter(group__teacher=teacher)

        group_id = self.request.query_params.get("group")
        if group_id:
            qs = qs.filter(group_id=group_id)
        return qs

    def perform_create(self, serializer):
        group = serializer.validated_data.get("group")
        if not self.request.user.is_staff:
            teacher = get_object_or_404(Teacher, owner=self.request.user)
            if group.teacher_id != teacher.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Bu guruh sizga tegishli emas")
        serializer.save()


class AttendanceView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsGroupTeacher]

    def perform_update(self, serializer):
        new_group = serializer.validated_data.get("group")
        if new_group is not None and not self.request.user.is_staff:
            teacher = get_object_or_404(Teacher, owner=self.request.user)
            if new_group.teacher_id != teacher.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Bu guruhga o'tkazishga ruxsatingiz yo'q")
        serializer.save()


class AttendanceRecordsView(APIView):
    permission_classes = [IsAuthenticated, IsGroupTeacher]

    def get(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        self.check_object_permissions(request, attendance)
        serializer = AttendanceRecordSerializer(attendance.records.all(), many=True)
        return Response(serializer.data)


class AttendanceMarkView(APIView):
    permission_classes = [IsAuthenticated, IsGroupTeacher]

    def post(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        self.check_object_permissions(request, attendance)

        student_id = request.data.get("student")
        status_value = request.data.get("status")

        if student_id is None or status_value is None:
            return Response(
                {"error": "student va status majburiy"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not attendance.group.students.filter(id=student_id).exists():
            return Response(
                {"error": "Bu student ushbu guruhga a'zo emas"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record, _ = AttendanceRecord.objects.update_or_create(
            attendance=attendance,
            student_id=student_id,
            defaults={"status": status_value},
        )
        serializer = AttendanceRecordSerializer(record)
        return Response(serializer.data)


class AttendanceRecordsListView(generics.ListCreateAPIView):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            teacher = get_object_or_404(Teacher, owner=user)
            qs = qs.filter(attendance__group__teacher_id=teacher.id)

        attendance_id = self.request.query_params.get("attendance")
        if attendance_id:
            qs = qs.filter(attendance_id=attendance_id)
        return qs

    def perform_create(self, serializer):
        attendance = serializer.validated_data.get("attendance")
        student = serializer.validated_data.get("student")
        if not self.request.user.is_staff:
            teacher = get_object_or_404(Teacher, owner=self.request.user)
            if attendance.group.teacher_id != teacher.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Bu guruh sizga tegishli emas")
        if not attendance.group.students.filter(id=student.id).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Bu student ushbu guruhga a'zo emas")
        serializer.save()


class AttendanceRecordView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsGroupTeacher]