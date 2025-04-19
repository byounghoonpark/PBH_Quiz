from django.db import models
from django.contrib.auth.models import User

from core.models import Grade

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    num_questions = models.PositiveIntegerField(help_text="응시 시 출제될 문제 수")
    shuffle_questions = models.BooleanField(default=True, help_text="문제 순서 랜덤 여부")
    shuffle_choices = models.BooleanField(default=True, help_text="선택지 순서 랜덤 여부")
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text