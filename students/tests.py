from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

class StudentAPITestCase(APITestCase):

    def setUp(self):
        # 1. Test uchun soxta Foydalanuvchi (User) yaratamiz
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword123'
        )
        # 2. Authenticate qilish (JWT/Session login o'rniga)
        self.client.force_authenticate(user=self.user)
        
        # 3. Test Student yaratib olamiz
        self.student = Student.objects.create(
            first_name="Ozodbek",
            last_name="Fayzullayev",
            phone_number="+998901234567",
            passport_number="AA1234567",
            owner=self.user
        )

    def test_get_students_list(self):
        """Talabalar ro'yxatini olish testi"""
        url = reverse('student-list')  # URL router nomingizga qarang
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_freeze_student(self):
        """Studentni freeze qilish API testi"""
        url = f"/api/v1/students/{self.student.id}/freeze/"
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, 'FROZEN')

    def test_unique_phone_validation(self):
        """Bir xil telefon raqam bilan qayta yaratib bo'lmaslik testi"""
        url = reverse('student-list')
        data = {
            "first_name": "Ali",
            "last_name": "Valiyev",
            "phone_number": "+998901234567", # Bir xil telefon
            "passport_number": "BB7654321",
            "owner": self.user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)