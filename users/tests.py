from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.models import Grade
from .models import UserProfile


class AuthFlowTestCase(APITestCase):
    def setUp(self):
        self.grade = Grade.objects.create(name="1학년")
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

    def test_register_user(self):
        payload = {
            "username": "newuser",
            "password": "securepassword123",
            "grade_id": self.grade.id
        }

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

        user = User.objects.get(username="newuser")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.grade, self.grade)

    def test_register_user_duplicate_username(self):
        User.objects.create_user(username="existing", password="pass123")
        payload = {
            "username": "existing",
            "password": "newpassword",
            "grade_id": self.grade.id
        }

        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_login_user_and_get_tokens(self):
        User.objects.create_user(username="loginuser", password="testpass123")
        payload = {
            "username": "loginuser",
            "password": "testpass123"
        }

        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        user = User.objects.create_user(username="refreshuser", password="refreshpass123")
        login_response = self.client.post(self.login_url, {
            "username": "refreshuser",
            "password": "refreshpass123"
        }, format='json')

        refresh_token = login_response.data.get("refresh")
        self.assertIsNotNone(refresh_token)

        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
