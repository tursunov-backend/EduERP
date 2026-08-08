from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Group
from .serializers import GroupSerializer, AssignTeacherSerializer, AddStudentSerializer
from teacher.models import Teacher
from students.models import Student

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['post'], url_path='assign-teacher')
    def assign_teacher(self, request, pk=None):
        group = self.get_object()
        serializer = AssignTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        teacher_id = serializer.validated_data['teacher_id']
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        group.teacher = teacher
        group.save()
        
        return Response({'detail': 'O\'qituvchi guruhga biriktirildi.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-student')
    def add_student(self, request, pk=None):
        group = self.get_object()
        serializer = AddStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_id = serializer.validated_data['student_id']
        student = get_object_or_404(Student, id=student_id)
        
        if group.students.filter(id=student_id).exists():
            return Response({'detail': 'Talaba allaqachon guruhda bor.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if group.students.count() >= group.max_student:
            return Response({'detail': 'Guruhda bo\'sh joy qolmagan.'}, status=status.HTTP_400_BAD_REQUEST)
            
        group.students.add(student)
        return Response({'detail': 'Talaba guruhga qo\'shildi.'}, status=status.HTTP_200_OK)