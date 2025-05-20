from rest_framework import serializers
from .models import BasicDetails
from .models import DemoQuestion

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = '__all__'

class DemoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoQuestion
        fields = ['id', 'question_text', 'question_type', 'options']

