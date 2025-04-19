from rest_framework import serializers
from .models import UserQuizSession
from quizzes.models import Question, Choice, Quiz


class UserQuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizSession
        fields = ['id', 'user', 'quiz', 'question_order', 'choice_order', 'answers', 'is_submitted', 'score', 'started_at', 'submitted_at']
        read_only_fields = ['user', 'quiz', 'question_order', 'choice_order', 'score', 'started_at', 'submitted_at']

class ChoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

    def get_choices(self, obj):
        session = self.context.get('session')
        choice_ids = session.choice_order.get(str(obj.id), [])
        choice_qs = list(Choice.objects.filter(id__in=choice_ids))
        # 순서 보장
        sorted_choices = sorted(choice_qs, key=lambda c: choice_ids.index(c.id))
        return ChoiceDetailSerializer(sorted_choices, many=True).data

class UserQuizSessionDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = UserQuizSession
        fields = ['id', 'quiz', 'is_submitted', 'score', 'started_at', 'submitted_at', 'answers', 'questions']

    def get_questions(self, obj):
        from quizzes.models import Question
        question_ids = obj.question_order
        question_qs = list(Question.objects.filter(id__in=question_ids))
        # 순서 보장
        sorted_questions = sorted(question_qs, key=lambda q: question_ids.index(q.id))
        return QuestionDetailSerializer(sorted_questions, many=True, context={'session': obj}).data


class SaveAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class QuizStatusSerializer(serializers.ModelSerializer):
    is_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'is_submitted']

    def get_is_submitted(self, quiz):
        session_map = self.context.get('session_map', {})
        return session_map.get(quiz.id, False)


class SubmitAnswerSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="문제 ID를 키, 선택지 ID를 값으로 갖는 딕셔너리 형태 예: {'1': 5, '2': 9}"
    )