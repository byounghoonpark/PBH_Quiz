from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import Grade
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    grade_id = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), source='profile.grade')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'grade_id']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user