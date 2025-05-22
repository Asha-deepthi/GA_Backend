from rest_framework import serializers
from .models import (
    BasicDetails, DemoQuestion, TestSession, Answer, ProctoringLog,
    ProctorComment, PageContent, BasicDetails, DemoQuestion
)

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = '__all__'

class DemoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoQuestion
        fields = '__all__'

class TestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class ProctoringLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctoringLog
        fields = '__all__'

class ProctorCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorComment
        fields = '__all__'

class PageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContent
        fields = '__all__'

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = '__all__'

class DemoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoQuestion
        fields = '__all__'
