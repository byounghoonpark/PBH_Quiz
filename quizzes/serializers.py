from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Quiz, Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

    def validate_choices(self, value):
        if len(value) < 3:
            raise ValidationError("각 문제는 최소 3개의 선택지를 가져야 합니다. (n+2 지선다)")
        correct_count = sum(1 for c in value if c.get('is_correct'))
        if correct_count != 1:
            raise ValidationError("각 문제는 정답이 정확히 1개여야 합니다.")
        return value

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'num_questions', 'shuffle_questions', 'shuffle_choices', 'created_by', 'created_at', 'questions', 'grade']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        for q in questions_data:
            choices_data = q.pop('choices')
            question = Question.objects.create(quiz=quiz, **q)
            for c in choices_data:
                Choice.objects.create(question=question, **c)
        return quiz


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'num_questions', 'shuffle_questions', 'shuffle_choices', 'created_by', 'created_at', 'grade']