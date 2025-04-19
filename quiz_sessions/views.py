from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions, status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Q
from quizzes.models import Quiz, Question
from .models import UserQuizSession
from .serializers import (
    UserQuizSessionSerializer,
    UserQuizSessionDetailSerializer,
    QuestionDetailSerializer,
    SaveAnswerSerializer,
    QuizStatusSerializer, SubmitAnswerSerializer
)
import random


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class StartQuizSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="퀴즈 응시 시작",
        operation_description="사용자가 퀴즈 응시를 시작합니다. 세션이 생성되고, 문제/선택지가 랜덤으로 배치됩니다.",
        responses={
            201: openapi.Response(description="세션 생성", examples={"application/json": {"session_id": 1}}),
            400: "학년 정보 없음 또는 접근 불가"
        }
    )
    def post(self, request, quiz_id):
        user = request.user
        profile = getattr(user, 'profile', None)

        if not profile or not profile.grade:
            return Response({"detail": "학년 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not Quiz.objects.filter(Q(grade__isnull=True) | Q(grade=profile.grade), id=quiz_id).exists():
            return Response({"detail": "학년에 맞는 퀴즈가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        quiz = get_object_or_404(Quiz, id=quiz_id)

        existing = UserQuizSession.objects.filter(user=user, quiz=quiz, is_submitted=False).first()
        if existing:
            return Response({'session_id': existing.id}, status=status.HTTP_200_OK)

        questions = list(quiz.questions.all())
        if quiz.shuffle_questions:
            random.shuffle(questions)
        questions = questions[:quiz.num_questions]
        question_order = [q.id for q in questions]

        choice_order = {}
        for question in questions:
            choices = list(question.choices.all())
            if quiz.shuffle_choices:
                random.shuffle(choices)
            choice_order[question.id] = [c.id for c in choices]

        session = UserQuizSession.objects.create(
            user=user,
            quiz=quiz,
            question_order=question_order,
            choice_order=choice_order,
        )
        return Response({'session_id': session.id}, status=status.HTTP_201_CREATED)


class SubmitQuizSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=SubmitAnswerSerializer,
        operation_summary="퀴즈 제출",
        operation_description="퀴즈 제출 후 자동 채점 및 결과 저장",
        responses={
            200: openapi.Response(description="제출 완료", examples={
                "application/json": {"session_id": 1, "score": 5, "submitted_at": "2024-01-01T12:00:00Z"}
            }),
            400: "이미 제출된 세션"
        }
    )
    def post(self, request, session_id):
        session = get_object_or_404(UserQuizSession, id=session_id, user=request.user)
        if session.is_submitted:
            return Response({'detail': '이미 제출된 세션입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        correct = 0
        for q_id_str, selected_cid in session.answers.items():
            try:
                question = Question.objects.get(id=int(q_id_str))
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice and correct_choice.id == selected_cid:
                    correct += 1
            except Question.DoesNotExist:
                continue

        session.score = correct
        session.is_submitted = True
        session.save(update_fields=["score", "is_submitted", "submitted_at"])

        return Response({
            'session_id': session.id,
            'score': session.score,
            'submitted_at': session.submitted_at
        }, status=status.HTTP_200_OK)


class SaveAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=SaveAnswerSerializer,
        operation_summary="퀴즈 답안 저장",
        operation_description="응시 중 선택한 답안을 임시 저장. 새로고침해도 유지됨.",
        responses={
            200: openapi.Response(description="저장 완료", examples={"application/json": {"status": "saved"}}),
            400: "입력 오류 또는 제출된 세션"
        }
    )
    def patch(self, request, session_id):
        serializer = SaveAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(UserQuizSession, id=session_id, user=request.user)
        if session.is_submitted:
            return Response({'detail': '이미 제출된 세션입니다.'}, status=400)

        question_id = str(request.data.get('question_id'))
        choice_id = request.data.get('choice_id')

        if question_id and choice_id:
            session.answers[question_id] = choice_id
            session.save(update_fields=['answers'])
            return Response({'status': 'saved'}, status=200)
        return Response({'detail': '입력 오류'}, status=400)


class UserQuizSessionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserQuizSessionDetailSerializer

    @swagger_auto_schema(
        operation_summary="퀴즈 세션 상세",
        responses={
            200: openapi.Response(
                description="세션 상세 정보",
                schema=UserQuizSessionDetailSerializer()
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserQuizSession.objects.none()
        return UserQuizSession.objects.filter(user=self.request.user)


class MyQuizStatusListView(CacheResponseMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizStatusSerializer
    pagination_class = Pagination

    @swagger_auto_schema(operation_summary="내 퀴즈 목록", responses={200: QuizStatusSerializer(many=True)})
    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)

        if not profile or not profile.grade:
            return Quiz.objects.none()

        return Quiz.objects.filter(
            models.Q(grade__isnull=True) |
            models.Q(grade=profile.grade)
        ).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        user = self.request.user
        session_map = {
            s.quiz_id: s.is_submitted
            for s in UserQuizSession.objects.filter(user=user)
        }
        context['session_map'] = session_map
        return context


class AdminQuizSessionListView(CacheResponseMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserQuizSessionSerializer
    pagination_class = Pagination

    @swagger_auto_schema(operation_summary="퀴즈별 응시 세션 조회 (관리자)", responses={200: UserQuizSessionSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        return UserQuizSession.objects.filter(quiz_id=quiz_id).order_by("id")


class PaginatedSessionQuestionView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionDetailSerializer
    pagination_class = Pagination

    @swagger_auto_schema(operation_summary="퀴즈 세션 문제 페이지 조회", responses={200: QuestionDetailSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        session = get_object_or_404(UserQuizSession, id=session_id, user=self.request.user)
        self.session = session
        question_ids = session.question_order
        question_qs = list(Question.objects.filter(id__in=question_ids))
        return sorted(question_qs, key=lambda q: question_ids.index(q.id))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        context['session'] = self.session
        return context
