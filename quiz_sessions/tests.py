from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from core.models import Grade
from users.models import UserProfile
from quizzes.models import Quiz, Question, Choice
from quiz_sessions.models import UserQuizSession


class QuizSessionAPITestCase(APITestCase):
    def setUp(self):
        self.grade = Grade.objects.create(name="1학년")
        self.admin = User.objects.create_superuser(username="admin", password="adminpass")
        self.user = User.objects.create_user(username="student", password="userpass")
        UserProfile.objects.create(user=self.user, grade=self.grade)

        self.quiz = Quiz.objects.create(
            title="테스트 퀴즈",
            description="설명",
            num_questions=2,
            shuffle_questions=False,
            shuffle_choices=False,
            grade=self.grade,
            created_by=self.admin
        )

        q1 = Question.objects.create(quiz=self.quiz, text="1+1=?")
        q2 = Question.objects.create(quiz=self.quiz, text="3-1=?")

        Choice.objects.bulk_create([
            Choice(question=q1, text="1", is_correct=False),
            Choice(question=q1, text="2", is_correct=True),
            Choice(question=q1, text="3", is_correct=False),
            Choice(question=q2, text="1", is_correct=False),
            Choice(question=q2, text="2", is_correct=True),
            Choice(question=q2, text="3", is_correct=False),
        ])

        self.login_as("student", "userpass")

    def login_as(self, username, password):
        response = self.client.post("/api/users/login/", {
            "username": username,
            "password": password
        }, format="json")
        self.assertEqual(response.status_code, 200)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def start_quiz(self):
        res = self.client.post(f"/api/sessions/{self.quiz.id}/start/")
        self.assertIn(res.status_code, [200, 201])
        return res.data["session_id"]

    def test_start_quiz_session(self):
        session_id = self.start_quiz()
        self.assertTrue(UserQuizSession.objects.filter(id=session_id).exists())

    def test_save_answer(self):
        session_id = self.start_quiz()
        session = UserQuizSession.objects.get(id=session_id)
        question_id = session.question_order[0]
        correct_choice = Question.objects.get(id=question_id).choices.filter(is_correct=True).first()

        res = self.client.patch(f"/api/sessions/sessions/{session_id}/answers/", {
            "question_id": question_id,
            "choice_id": correct_choice.id
        }, format='json')
        self.assertEqual(res.status_code, 200)

    def test_submit_quiz(self):
        session_id = self.start_quiz()
        session = UserQuizSession.objects.get(id=session_id)
        for qid in session.question_order:
            correct = Question.objects.get(id=qid).choices.filter(is_correct=True).first()
            session.answers[str(qid)] = correct.id
        session.save()

        res = self.client.post(f"/api/sessions/sessions/{session_id}/submit/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["score"], 2)

    def test_get_session_detail(self):
        session_id = self.start_quiz()
        res = self.client.get(f"/api/sessions/sessions/{session_id}/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("questions", res.data)

    def test_get_paginated_questions(self):
        session_id = self.start_quiz()
        res = self.client.get(f"/api/sessions/sessions/{session_id}/questions/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)

    def test_get_my_quiz_status_list(self):
        self.start_quiz()
        res = self.client.get("/api/sessions/my_list/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)

    def test_admin_can_get_all_sessions_for_quiz(self):
        self.start_quiz()
        self.login_as("admin", "adminpass")
        res = self.client.get(f"/api/sessions/admin/{self.quiz.id}/sessions/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)
