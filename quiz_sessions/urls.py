# quiz_sessions/urls.py
from django.urls import path
from .views import (
    StartQuizSessionView,
    SubmitQuizSessionView,
    SaveAnswerView,
    UserQuizSessionDetailView,
    MyQuizStatusListView,
    AdminQuizSessionListView,
    PaginatedSessionQuestionView,
)

urlpatterns = [
    path('<int:quiz_id>/start/', StartQuizSessionView.as_view(), name='quiz-start'),
    path('sessions/<int:session_id>/submit/', SubmitQuizSessionView.as_view(), name='quiz-submit'),
    path('sessions/<int:session_id>/answers/', SaveAnswerView.as_view(), name='quiz-answer-save'),
    path('sessions/<int:pk>/', UserQuizSessionDetailView.as_view(), name='quiz-session-detail'),
    path('sessions/<int:session_id>/questions/', PaginatedSessionQuestionView.as_view(), name='quiz-session-paged-questions'),
    path('my_list/', MyQuizStatusListView.as_view(), name='my-quiz-status'),
    path('admin/<int:quiz_id>/sessions/', AdminQuizSessionListView.as_view(), name='admin-quiz-sessions'),
]
