from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import ChangePasswordView, CreateAdminView, CreateTeacherView, CreateStudentView, LoginView, LogoutView, MeView


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
    "create-admin/",
        CreateAdminView.as_view(),
        name="create-admin",
    ),
    path(
        "create-teacher/",
        CreateTeacherView.as_view(),
        name="create-teacher",
    ),
    path(
        "create-student/",
        CreateStudentView.as_view(),
        name="create-student",
    ),
]