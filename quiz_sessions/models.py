from django.db import models
from django.contrib.auth.models import User
from quizzes.models import Quiz
from django.utils import timezone

class UserQuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_order = models.JSONField()
    choice_order = models.JSONField()
    answers = models.JSONField(default=dict)
    is_submitted = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"

    def calculate_score(self):
        from quizzes.models import Choice
        total = 0
        for qid, cid in self.answers.items():
            try:
                correct = Choice.objects.get(question_id=qid, is_correct=True)
                if correct.id == cid:
                    total += 1
            except Choice.DoesNotExist:
                continue
        return total

    def save(self, *args, **kwargs):
        if self.is_submitted and self.score is None:
            self.score = self.calculate_score()
            self.submitted_at = self.submitted_at or timezone.now()
        super().save(*args, **kwargs)