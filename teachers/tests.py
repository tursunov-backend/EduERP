from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from groups.models import Group, Lessons
from students.models import Student
from .models import (
    Teacher,
    Subject,
    TeacherWorkload,
    Transaction,
    Contract,
    HomeWork,
    StudentGamification,
)

User = get_user_model()


class BaseTeacherTestCase(APITestCase):
    """Umumiy setup: userlar va boshlang'ich obyektlar."""

    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner", password="testpass123", is_staff=True
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123", is_staff=True
        )
        self.staff_user = User.objects.create_user(
            username="staff", password="testpass123", is_staff=True
        )
        self.user = User.objects.create_superuser(
            username='admin_test',
            password='password123'
        )

        self.subject_math = Subject.objects.create(name="Matematika")
        self.subject_phys = Subject.objects.create(name="Fizika")

        self.teacher = Teacher.objects.create(
            first_name="Aziz",
            last_name="Qodirov",
            owner=self.owner_user,
            amount=1500000,
            salary_type=Teacher.SalaryType.MONTHLY,
        )
        self.teacher.subjects.add(self.subject_math)

        self.group = Group.objects.create(name="9-A")
        
        # Qattiq sana o'rniga dinamik bugungi sana
        self.today = date.today()
        self.lesson = Lessons.objects.create(
            group=self.group, date=self.today
        )
        self.student_user = User.objects.create_user(
            username="sardor_student", password="testpass123", first_name="Sardor", last_name="Aliyev"
        )
        self.student = Student.objects.create(
            first_name="Sardor", 
            last_name="Aliyev"
        )


class SubjectAPITests(BaseTeacherTestCase):

    def test_list_subjects_requires_auth(self):
        url = reverse("subjects")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_subjects_authenticated(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("subjects")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_subject(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("subjects")
        response = self.client.post(url, {"name": "Kimyo"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subject.objects.count(), 3)

    def test_create_subject_duplicate_name_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("subjects")
        response = self.client.post(url, {"name": "Matematika"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_update_delete_subject(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("subject", args=[self.subject_phys.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Fizika")

        response = self.client.patch(url, {"name": "Fizika (yangi)"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subject_phys.refresh_from_db()
        self.assertEqual(self.subject_phys.name, "Fizika (yangi)")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subject.objects.filter(id=self.subject_phys.id).exists())


class TeacherAPITests(BaseTeacherTestCase):

    def test_list_teachers_requires_auth(self):
        url = reverse("teachers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_teachers(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("teachers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_teacher_sets_owner_automatically(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("teachers")
        payload = {
            "first_name": "Malika",
            "last_name": "Yusupova",
            "bio": "Ingliz tili o'qituvchisi",
            "amount": "1200000",
            "salary_type": Teacher.SalaryType.PER_LESSON,
            "subject_ids": [self.subject_phys.id],
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Teacher.objects.get(id=response.data["id"])
        self.assertEqual(created.owner, self.other_user)
        self.assertEqual(list(created.subjects.all()), [self.subject_phys])

    def test_retrieve_teacher(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Aziz")

    def test_owner_can_update_own_teacher(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.patch(url, {"bio": "Yangilangan bio"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.bio, "Yangilangan bio")

    def test_non_owner_cannot_update_teacher(self):
        non_owner = User.objects.create_user(username="non_owner_user", password="testpass123", is_staff=False)
        self.client.force_authenticate(user=non_owner)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.patch(url, {"bio": "Ruxsatsiz yozuv"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_any_teacher(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.patch(url, {"bio": "Staff tomonidan tahrirlandi"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_delete_teacher(self):
        non_owner = User.objects.create_user(username="non_owner_user2", password="testpass123", is_staff=False)
        self.client.force_authenticate(user=non_owner)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Teacher.objects.filter(id=self.teacher.id).exists())

    def test_owner_can_delete_own_teacher(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Teacher.objects.filter(id=self.teacher.id).exists())

    def test_anyone_can_read_teacher_detail(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("teacher", args=[self.teacher.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MyTeacherProfileAPITests(BaseTeacherTestCase):

    def test_get_my_profile(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("my-teacher-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.teacher.id)

    def test_get_my_profile_not_found(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("my-teacher-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_my_profile(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("my-teacher-profile")
        response = self.client.patch(url, {"bio": "Mening yangi bio'im"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.bio, "Mening yangi bio'im")

    def test_unauthenticated_cannot_access_my_profile(self):
        self.client.logout()
        url = reverse("my-teacher-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TeacherWorkloadAPITests(BaseTeacherTestCase):

    def setUp(self):
        super().setUp()
        self.workload = TeacherWorkload.objects.create(
            teacher=self.teacher, group=self.group, hours_per_week=6
        )

    def test_list_workloads(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workloads")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_workloads_by_teacher(self):
        other_teacher = Teacher.objects.create(
            first_name="Nodira", last_name="Karimova", owner=self.other_user
        )
        TeacherWorkload.objects.create(
            teacher=other_teacher, group=self.group, hours_per_week=4
        )

        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workloads")
        response = self.client.get(url, {"teacher": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["teacher"], self.teacher.id)

    def test_create_workload(self):
        new_group = Group.objects.create(name="10-B")
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workloads")
        payload = {
            "teacher": self.teacher.id,
            "group": new_group.id,
            "hours_per_week": 8,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TeacherWorkload.objects.count(), 2)

    def test_create_duplicate_workload_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workloads")
        payload = {
            "teacher": self.teacher.id,
            "group": self.group.id,
            "hours_per_week": 10,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_workload(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workload", args=[self.workload.id])
        response = self.client.patch(url, {"hours_per_week": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workload.refresh_from_db()
        self.assertEqual(self.workload.hours_per_week, 10)

    def test_delete_workload(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("workload", args=[self.workload.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeacherWorkload.objects.filter(id=self.workload.id).exists())


class TransactionAPITests(BaseTeacherTestCase):

    def setUp(self):
        super().setUp()
        self.transaction = Transaction.objects.create(
            teacher=self.teacher,
            transaction_type=Transaction.TransactionType.SALARY,
            amount=1500000,
            comment="Maosh",
        )

    def test_list_transactions_ordered_by_date_desc(self):
        Transaction.objects.create(
            teacher=self.teacher,
            transaction_type=Transaction.TransactionType.BONUS,
            amount=200000,
        )
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("transactions")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["transaction_type"], "bonus")

    def test_filter_transactions_by_teacher(self):
        other_teacher = Teacher.objects.create(
            first_name="Nodira", last_name="Karimova", owner=self.other_user
        )
        Transaction.objects.create(
            teacher=other_teacher,
            transaction_type=Transaction.TransactionType.PENALTY,
            amount=50000,
        )
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("transactions")
        response = self.client.get(url, {"teacher": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_transaction(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("transactions")
        payload = {
            "teacher": self.teacher.id,
            "transaction_type": Transaction.TransactionType.PENALTY,
            "amount": "50000",
            "comment": "Kechikish uchun jarima",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_create_transaction_invalid_type_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("transactions")
        payload = {
            "teacher": self.teacher.id,
            "transaction_type": "invalid_type",
            "amount": "50000",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_transaction(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("transaction", args=[self.transaction.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())


class ContractAPITests(BaseTeacherTestCase):

    def setUp(self):
        super().setUp()
        self.contract = Contract.objects.create(
            teacher=self.teacher,
            number="C-001",
            start_date=self.today,
        )

    def test_list_contracts(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contracts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_contracts_by_teacher(self):
        other_teacher = Teacher.objects.create(
            first_name="Nodira", last_name="Karimova", owner=self.other_user
        )
        Contract.objects.create(
            teacher=other_teacher, number="C-002", start_date=self.today
        )
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contracts")
        response = self.client.get(url, {"teacher": self.teacher.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_contract(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contracts")
        payload = {
            "teacher": self.teacher.id,
            "number": "C-003",
            "start_date": str(self.today),
            "is_active": True,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contract.objects.count(), 2)

    def test_create_contract_duplicate_number_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contracts")
        payload = {
            "teacher": self.teacher.id,
            "number": "C-001",
            "start_date": str(self.today),
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_contract(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contract", args=[self.contract.id])
        response = self.client.patch(url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contract.refresh_from_db()
        self.assertFalse(self.contract.is_active)

    def test_delete_contract(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("contract", args=[self.contract.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contract.objects.filter(id=self.contract.id).exists())


class HomeWorkAPITests(BaseTeacherTestCase):

    def setUp(self):
        super().setUp()
        # Dinamik ravishda kelajakdagi 7 kun keyingi muddatni beramiz
        self.due_date = timezone.now() + timedelta(days=7)
        self.homework = HomeWork.objects.create(
            lesson=self.lesson,
            description="1-10 mashqlarni yeching",
            max_score=100,
            due_date=self.due_date,
        )

    def test_list_homeworks(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homeworks")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_homeworks_requires_auth(self):
        self.client.logout()
        url = reverse("homeworks")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_homeworks_by_lesson(self):
        other_lesson = Lessons.objects.create(group=self.group, date=self.today + timedelta(days=1))
        HomeWork.objects.create(
            lesson=other_lesson,
            description="Boshqa dars uy vazifasi",
            max_score=50,
            due_date=self.due_date,
        )
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homeworks")
        response = self.client.get(url, {"lesson": self.lesson.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_homework(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homeworks")
        payload = {
            "lesson": self.lesson.id,
            "description": "Insho yozish",
            "max_score": 20,
            "status": HomeWork.Status.PUBLISHED,
            "due_date": (timezone.now() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HomeWork.objects.count(), 2)

    def test_create_homework_missing_required_field_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homeworks")
        payload = {"lesson": self.lesson.id, "max_score": 20}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_homework(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homework", args=[self.homework.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "1-10 mashqlarni yeching")

    def test_update_homework_status(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homework", args=[self.homework.id])
        response = self.client.patch(url, {"status": HomeWork.Status.CLOSED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.homework.refresh_from_db()
        self.assertEqual(self.homework.status, HomeWork.Status.CLOSED)

    def test_delete_homework(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("homework", args=[self.homework.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HomeWork.objects.filter(id=self.homework.id).exists())


class StudentGamificationAPITests(BaseTeacherTestCase):

    def setUp(self):
        super().setUp()
        self.gamification = StudentGamification.objects.create(
            student=self.student, xp=150, level=2
        )

    def test_list_gamifications(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamifications")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_gamification_by_student(self):
        other_student = Student.objects.create(first_name="Laylo", last_name="Karimova")
        StudentGamification.objects.create(student=other_student, xp=10, level=1)

        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamifications")
        response = self.client.get(url, {"student": self.student.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["xp"], 150)

    def test_create_gamification(self):
        new_student = Student.objects.create(first_name="Jasur", last_name="Toshev")
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamifications")
        payload = {"student": new_student.id, "xp": 0, "level": 1}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentGamification.objects.count(), 2)

    def test_create_duplicate_gamification_for_same_student_fails(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamifications")
        payload = {"student": self.student.id, "xp": 5, "level": 1}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_gamification(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamification", args=[self.gamification.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["level"], 2)

    def test_update_gamification_xp(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamification", args=[self.gamification.id])
        response = self.client.patch(url, {"xp": 500, "level": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.gamification.refresh_from_db()
        self.assertEqual(self.gamification.xp, 500)
        self.assertEqual(self.gamification.level, 5)

    def test_delete_gamification(self):
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("gamification", args=[self.gamification.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            StudentGamification.objects.filter(id=self.gamification.id).exists()
        )