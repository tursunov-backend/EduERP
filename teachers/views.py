from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from .models import (
    Teacher,
    Subject,
    TeacherWorkload,
    Transaction,
    Contract,
    HomeWork,
    StudentGamification,
    Exam,
    ExamResult,
)
from .serializers import (
    TeacherSerializer,
    SubjectSerializer,
    TeacherWorkloadSerializer,
    TransactionSerializer,
    ContractSerializer,
    HomeWorkSerializer,
    StudentGamificationSerializer,
    ExamSerializer,
    ExamResultSerializer,
)
from .permissions import (
    IsOwnerOrReadOnlyForStaff,
    IsRelatedTeacherOwner,
    IsStaffOrReadOnly,
    TeacherScopedQuerysetMixin,
)


def _own_teacher(request):
    """So'rov yuborgan foydalanuvchining o'z Teacher profilini qaytaradi."""
    return Teacher.objects.filter(owner=request.user).first()


def _has_workload_for_group(teacher, group):
    return (
        teacher is not None
        and group is not None
        and TeacherWorkload.objects.filter(teacher=teacher, group=group).exists()
    )


class TeachersView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if Teacher.objects.filter(owner=self.request.user).exists():
            raise ValidationError(
                {"detail": "Sizda allaqachon teacher profili mavjud."}
            )
        serializer.save(owner=self.request.user)


class TeacherView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyForStaff]


class MyTeacherProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Teacher.objects.get(owner=self.request.user)
        except Teacher.DoesNotExist:
            raise NotFound("Sizga tegishli teacher profili topilmadi")


class SubjectsView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsStaffOrReadOnly]


class SubjectView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsStaffOrReadOnly]


class TeacherWorkloadsView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = TeacherWorkloadSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(TeacherWorkload.objects.all())
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            target_teacher = serializer.validated_data.get("teacher")
            if own_teacher is None or target_teacher is None or target_teacher.id != own_teacher.id:
                raise PermissionDenied("Faqat o'zingizga tegishli workload yarata olasiz")
        serializer.save()


class TeacherWorkloadView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherWorkload.objects.all()
    serializer_class = TeacherWorkloadSerializer
    teacher_lookup = "teacher_id"
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]

    def perform_update(self, serializer):
        new_teacher = serializer.validated_data.get("teacher")
        if new_teacher is not None and not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            if own_teacher is None or new_teacher.id != own_teacher.id:
                raise PermissionDenied("Teacher maydonini o'zgartirishga ruxsat yo'q")
        serializer.save()


class TransactionsView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(Transaction.objects.all().order_by("-date_added"))
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Tranzaksiya yaratish faqat administratorlar uchun")
        serializer.save()


class TransactionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    teacher_lookup = "teacher_id"
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Tranzaksiyani tahrirlash faqat administratorlar uchun")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Tranzaksiyani o'chirish faqat administratorlar uchun")
        instance.delete()


class ContractsView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(Contract.objects.all())
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Shartnoma yaratish faqat administratorlar uchun")
        serializer.save()


class ContractView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    teacher_lookup = "teacher_id"
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Shartnomani tahrirlash faqat administratorlar uchun")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Shartnomani o'chirish faqat administratorlar uchun")
        instance.delete()


class HomeWorksView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = HomeWorkSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "lesson__group__workloads__teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(HomeWork.objects.all().order_by("-created_at"))
        qs = qs.distinct()  
        lesson_id = self.request.query_params.get("lesson")
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs

    def perform_create(self, serializer):
        lesson = serializer.validated_data.get("lesson")
        if not self.request.user.is_staff:
            own_teacher = Teacher.objects.filter(owner=self.request.user).first()
            group = getattr(lesson, "group", None)
            has_workload = (
                own_teacher is not None
                and group is not None
                and TeacherWorkload.objects.filter(teacher=own_teacher, group=group).exists()
            )
            if not has_workload:
                raise PermissionDenied("Faqat o'z darsingiz uchun uy vazifa qo'sha olasiz")
        serializer.save()


class HomeWorkView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HomeWork.objects.all()
    serializer_class = HomeWorkSerializer
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]
    teacher_lookup = "lesson__group__workloads__teacher_id"

    def perform_update(self, serializer):
        new_lesson = serializer.validated_data.get("lesson")
        if new_lesson is not None and not self.request.user.is_staff:
            own_teacher = Teacher.objects.filter(owner=self.request.user).first()
            group = getattr(new_lesson, "group", None)
            has_workload = (
                own_teacher is not None
                and group is not None
                and TeacherWorkload.objects.filter(teacher=own_teacher, group=group).exists()
            )
            if not has_workload:
                raise PermissionDenied("Faqat o'z darsingizga tegishli qilib o'zgartira olasiz")
        serializer.save()


class StudentGamificationsView(generics.ListCreateAPIView):
    serializer_class = StudentGamificationSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = StudentGamification.objects.all()
        student_id = self.request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class StudentGamificationView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentGamification.objects.all()
    serializer_class = StudentGamificationSerializer
    permission_classes = [IsStaffOrReadOnly]


class ExamsView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "lesson__group__workloads__teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(Exam.objects.all().order_by("-exam_date"))
        qs = qs.distinct()  
        lesson_id = self.request.query_params.get("lesson")
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs

    def perform_create(self, serializer):
        lesson = serializer.validated_data.get("lesson")
        if not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            group = getattr(lesson, "group", None)
            if not _has_workload_for_group(own_teacher, group):
                raise PermissionDenied("Faqat o'z darsingiz uchun imtihon qo'sha olasiz")
        serializer.save()


class ExamView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]
    teacher_lookup = "lesson__group__workloads__teacher_id"

    def perform_update(self, serializer):
        new_lesson = serializer.validated_data.get("lesson")
        if new_lesson is not None and not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            group = getattr(new_lesson, "group", None)
            if not _has_workload_for_group(own_teacher, group):
                raise PermissionDenied("Faqat o'z darsingizga tegishli qilib o'zgartira olasiz")
        serializer.save()


class ExamResultsView(TeacherScopedQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    teacher_lookup = "exam__lesson__group__workloads__teacher_id"

    def get_queryset(self):
        qs = self.scope_to_teacher(ExamResult.objects.all().order_by("-graded_at"))
        qs = qs.distinct()
        exam_id = self.request.query_params.get("exam")
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        student_id = self.request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        exam = serializer.validated_data.get("exam")
        if not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            group = getattr(getattr(exam, "lesson", None), "group", None)
            if not _has_workload_for_group(own_teacher, group):
                raise PermissionDenied("Faqat o'z imtihoningiz uchun natija qo'sha olasiz")
        serializer.save()


class ExamResultView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated, IsRelatedTeacherOwner]
    teacher_lookup = "exam__lesson__group__workloads__teacher_id"

    def perform_update(self, serializer):
        new_exam = serializer.validated_data.get("exam")
        if new_exam is not None and not self.request.user.is_staff:
            own_teacher = _own_teacher(self.request)
            group = getattr(getattr(new_exam, "lesson", None), "group", None)
            if not _has_workload_for_group(own_teacher, group):
                raise PermissionDenied("Faqat o'z imtihoningizga tegishli qilib o'zgartira olasiz")
        serializer.save()