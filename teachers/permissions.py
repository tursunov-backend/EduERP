from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Teacher


class IsOwnerOrReadOnlyForStaff(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id or request.user.is_staff


class IsStaffOrReadOnly(BasePermission):
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsRelatedTeacherOwner(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        teacher = Teacher.objects.filter(owner=request.user).first()
        if teacher is None:
            return False

        lookup = getattr(view, "teacher_lookup", "teacher_id")
        parts = lookup.split("__")
        value = obj

        for i, attr in enumerate(parts):
            if value is None:
                return False
            
            manager_all = getattr(value, "all", None)
            if callable(manager_all):
                remaining_lookup = "__".join(parts[i:])
                return value.filter(**{remaining_lookup: teacher.id}).exists()

            value = getattr(value, attr, None)

        if hasattr(value, "id"):
            value = value.id

        return value == teacher.id


class TeacherScopedQuerysetMixin:

    teacher_lookup = "teacher_id"

    def scope_to_teacher(self, queryset):
        user = self.request.user
        if user.is_staff:
            return queryset

        teacher = Teacher.objects.filter(owner=user).first()
        if teacher is None:
            return queryset.none()

        return queryset.filter(**{self.teacher_lookup: teacher.id})