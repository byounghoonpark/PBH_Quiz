from django.contrib.auth.models import User
from django.db import models

from core.models import Grade


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.grade}학년 - {self.user.username}"
