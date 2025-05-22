from rest_framework import serializers
from .models import (
    BasicDetails, DemoQuestion, TestSession, Answer, ProctoringLog,
    ProctorComment, PageContent, BasicDetails, DemoQuestion, AudioResponse, VideoResponse
)

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = ['id', 'name', 'email', 'phone_number']

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

class AudioResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioResponse
        fields = ['id', 'user', 'audio_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'user']

class VideoResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoResponse
        fields = '__all__'

