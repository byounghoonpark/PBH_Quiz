# core/models.py
from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=20, unique=True)  # 예: "1학년", "2학년"

    def __str__(self):
        return self.name
