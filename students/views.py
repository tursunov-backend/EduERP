from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin, IsTeacher, IsStudent
from .models import Student
from .serializers import StudentSerializer, StudentCreateUpdateSerializer, TransferStudentSerializer
from .services import StudentService



def custom_response(data=None, message="", success=True, status_code=200):
    return Response({
        "success": success,
        "message": message,
        "data": data if data is not None else {}
    }, status=status_code)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['first_name', 'last_name', 'phone_number', 'passport_number']

    def get_queryset(self):
        user = self.request.user

        if getattr(user, 'role', None) == 'student':
            return Student.objects.filter(owner=self.request.user)

        return Student.objects.all().order_by('-id')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, (IsAdmin | IsTeacher | IsStudent)]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentCreateUpdateSerializer
        return StudentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True) # <-- Bu yerda 'page' bo'lishi kerak
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data, message="Talabalar ro'yxati")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return custom_response(
            data=StudentSerializer(student).data,
            message="Talaba muvaffaqiyatli yaratildi",
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='freeze')
    def freeze(self, request, pk=None):
        student = self.get_object()
        update_student = StudentService.freeze_student(student)
        return custom_response(
            data=StudentSerializer(update_student).data,
            message="Talaba muzlatildi."
        )

    @action(detail=True, methods=['post'], url_path='unfreeze')
    def unfreeze(self, request, pk=None):
        student = self.get_object()
        updated_student = StudentService.unfreeze_student(student)
        return custom_response(
            data=StudentSerializer(updated_student).data,
            message="Talaba aktivlashtirildi."
        )

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        student = self.get_object()
        updated_student = StudentService.archive_student(student)
        return custom_response(
            data=StudentSerializer(updated_student).data,
            message="Talaba arxivga o'tkazildi."
        )