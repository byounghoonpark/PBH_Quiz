from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from quizzes.models import Quiz
from core.models import Grade


class QuizAdminViewSetTest(APITestCase):
    def setUp(self):
        self.grade = Grade.objects.create(name="1학년")

        # 관리자 유저
        self.admin = User.objects.create_user(username="admin", password="adminpass", is_staff=True, is_superuser=True)

        # 일반 사용자
        self.user = User.objects.create_user(username="student", password="userpass")

        self.quiz_payload = {
            "title": "과학 퀴즈",
            "description": "과학 관련 문제입니다.",
            "num_questions": 3,
            "shuffle_questions": True,
            "shuffle_choices": True,
            "grade": self.grade.id
        }

    def login_as(self, username, password):
        res = self.client.post("/api/users/login/", {
            "username": username,
            "password": password
        }, format="json")
        self.assertEqual(res.status_code, 200)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_quiz_as_admin(self):
        self.login_as("admin", "adminpass")
        res = self.client.post("/api/quizzes/admin/quizzes/", self.quiz_payload, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Quiz.objects.count(), 1)

    def test_list_quizzes_as_admin(self):
        self.login_as("admin", "adminpass")
        Quiz.objects.create(
            title="기존 퀴즈",
            description="이건 테스트용 퀴즈",
            num_questions=1,
            shuffle_questions=False,
            shuffle_choices=False,
            grade=self.grade,
            created_by=self.admin
        )
        res = self.client.get("/api/quizzes/admin/quizzes/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_retrieve_quiz_as_admin(self):
        self.login_as("admin", "adminpass")
        quiz = Quiz.objects.create(
            title="기본 퀴즈",
            description="단일 퀴즈입니다.",
            num_questions=2,
            shuffle_questions=True,
            shuffle_choices=True,
            grade=self.grade,
            created_by=self.admin
        )
        res = self.client.get(f"/api/quizzes/admin/quizzes/{quiz.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], quiz.id)

    def test_update_quiz_as_admin(self):
        self.login_as("admin", "adminpass")
        quiz = Quiz.objects.create(
            title="업데이트 전",
            description="변경 전 설명",
            num_questions=2,
            shuffle_questions=True,
            shuffle_choices=True,
            grade=self.grade,
            created_by=self.admin
        )
        res = self.client.put(f"/api/quizzes/admin/quizzes/{quiz.id}/", {
            **self.quiz_payload,
            "title": "업데이트 후",
        }, format="json")
        self.assertEqual(res.status_code, 200)
        quiz.refresh_from_db()
        self.assertEqual(quiz.title, "업데이트 후")

    def test_delete_quiz_as_admin(self):
        self.login_as("admin", "adminpass")
        quiz = Quiz.objects.create(
            title="삭제용 퀴즈",
            description="삭제 대상",
            num_questions=1,
            shuffle_questions=True,
            shuffle_choices=True,
            grade=self.grade,
            created_by=self.admin
        )
        res = self.client.delete(f"/api/quizzes/admin/quizzes/{quiz.id}/")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())

    def test_user_cannot_access_admin_quiz_apis(self):
        self.login_as("student", "userpass")

        # Create
        res = self.client.post("/api/quizzes/admin/quizzes/", self.quiz_payload, format="json")
        self.assertEqual(res.status_code, 403)

        # List
        res = self.client.get("/api/quizzes/admin/quizzes/")
        self.assertEqual(res.status_code, 403)

        # Retrieve
        res = self.client.get("/api/quizzes/admin/quizzes/1/")
        self.assertEqual(res.status_code, 403)

        # Update
        res = self.client.put("/api/quizzes/admin/quizzes/1/", self.quiz_payload, format="json")
        self.assertEqual(res.status_code, 403)

        # Delete
        res = self.client.delete("/api/quizzes/admin/quizzes/1/")
        self.assertEqual(res.status_code, 403)
