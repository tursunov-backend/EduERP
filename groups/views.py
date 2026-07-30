from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Group, GroupStudent
from .serializers import GroupSerializer, AssignTeacherSerializer, AddStudentSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['patch'], serializer_class=AssignTeacherSerializer)
    def assign_teacher(self, request, pk=None):
        group = self.get_object()
        teacher_id = request.data.get('teacher_id')
        
        if not teacher_id:
            return Response({"error": "teacher_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        group.teacher_id = teacher_id
        group.save()
        return Response({"success": True, "message": "O'qituvchi muvaffaqiyatli biriktirildi", "data": GroupSerializer(group).data})

    @action(detail=True, methods=['post'], serializer_class=AddStudentSerializer)
    def add_student(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if group.enrollments.filter(status='active').count() >= group.max_students:
            return Response({"error": "Guruh to'lgan. Maksimal sig'im: 20 ta student."}, status=status.HTTP_400_BAD_REQUEST)

        if GroupStudent.objects.filter(group=group, student_id=student_id).exists():
            return Response({"error": "Bu student guruhda allaqachon mavjud."}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = GroupStudent.objects.create(group=group, student_id=student_id)
        
        return Response({
            "success": True, 
            "message": "Student guruhga muvaffaqiyatli qo'shildi", 
            "data": {"enrollment_id": enrollment.id}
        }, status=status.HTTP_201_CREATED)