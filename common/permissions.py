from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )
    

class IsAdmin(BasePermission):
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsTeacher(BasePermission):
    message = "Only teachers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudent(BasePermission):
    message = "Only students can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"