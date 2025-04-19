from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuizAdminViewSet

router = DefaultRouter()
router.register(r'admin/quizzes', QuizAdminViewSet, basename='admin-quizzes')

urlpatterns = [
    path('', include(router.urls)),
    # path('list/', QuizListView.as_view(), name='quiz-list'),
    # path('<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),

]
