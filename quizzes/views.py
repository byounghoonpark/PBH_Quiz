from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from django.db import models
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Quiz
from .serializers import QuizSerializer, QuizListSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuizAdminViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAdminUser]
    pagination_class = Pagination

    @swagger_auto_schema(operation_summary="퀴즈 목록 조회 (관리자)")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="퀴즈 생성 (관리자)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="퀴즈 상세 조회 (관리자)")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="퀴즈 수정 (관리자)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="퀴즈 삭제 (관리자)")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# class QuizListView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = QuizSerializer
#     pagination_class = Pagination
#
#     @swagger_auto_schema(operation_summary="사용자 퀴즈 목록 조회")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#     def get_queryset(self):
#         user: User = self.request.user
#         profile = getattr(user, 'profile', None)
#         if not profile:
#             return Quiz.objects.none()
#
#         return Quiz.objects.filter(
#             models.Q(grade__isnull=True) |
#             (models.Q(grade=profile.grade) & (
#                 models.Q(classroom__isnull=True) | models.Q(classroom=profile.classroom)
#             ))
#         ).order_by('-created_at')
#
#
# class QuizDetailView(RetrieveAPIView):
#     serializer_class = QuizSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(operation_summary="퀴즈 상세 조회")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#     def get_queryset(self):
#         user = self.request.user
#         profile = user.profile
#         return Quiz.objects.filter(
#             models.Q(grade__isnull=True) |
#             (models.Q(grade=profile.grade) & (
#                 models.Q(classroom__isnull=True) | models.Q(classroom=profile.classroom)
#             ))
#         )
