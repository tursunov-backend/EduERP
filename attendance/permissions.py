from rest_framework.permissions import BasePermission
from teachers.models import Teacher


class IsGroupTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        attendance = obj if hasattr(obj, "group") else obj.attendance
        try:
            teacher = Teacher.objects.get(owner=request.user)
        except Teacher.DoesNotExist:
            return False
        return attendance.group.teacher_id == teacher.id