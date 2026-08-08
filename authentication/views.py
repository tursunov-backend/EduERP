from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.permissions import IsAdmin, IsSuperUser

from .serializer import ChangePasswordSerializer, CreateAdminSerializer, CreateStudentSerializer, CreateTeacherSerializer, LoginSerializer, MeSerializer, LogoutSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT,
        )

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.save()

        return Response(
            {
                "detail": "Password changed successfully.",
                **tokens,
            },
            status=status.HTTP_200_OK,
        )


class CreateAdminView(generics.CreateAPIView):
    serializer_class = CreateAdminSerializer
    permission_classes = [
        IsAuthenticated,
        IsSuperUser,
    ]


class CreateTeacherView(generics.CreateAPIView):
    serializer_class = CreateTeacherSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]


class CreateStudentView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]