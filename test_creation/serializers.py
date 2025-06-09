from rest_framework import serializers
from .models import Test, Section, Question, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'text', 'is_correct', 'order_index']
        
class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('created_by',)
        extra_kwargs = {
            'correct_answers': {'required': False, 'allow_null': True},
            'passage_text': {'required': False, 'allow_blank': True, 'allow_null': True},
            'video_time': {'required': False, 'allow_null': True},
            'audio_time': {'required': False, 'allow_null': True},
        }
class SectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ('created_by',)

class TestSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('created_by',)
