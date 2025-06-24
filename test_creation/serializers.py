from rest_framework import serializers
from .models import Test, Section, Question, Option
from .models import Candidate_Test
from users.models import Candidate
import hashlib
import random

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'text', 'is_correct']
        
class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()  # 👈 dynamic field

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

    def get_options(self, obj):
        request = self.context.get('request')
        candidate_test_id = request.query_params.get('candidate_test_id') if request else None

        options = list(obj.options.all())

        # Check if we should shuffle
        if obj.section.shuffle_answers and candidate_test_id:
            # Deterministic shuffle per question and candidate
            seed = int(hashlib.sha256(f"{candidate_test_id}-{obj.id}".encode()).hexdigest(), 16) % (10 ** 8)
            rng = random.Random(seed)
            rng.shuffle(options)

        return OptionSerializer(options, many=True).data

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

#class TestAssignmentSerializer(serializers.ModelSerializer):
    # For a richer response, we can show details from the linked models
 #   candidate_name = serializers.CharField(source='candidate.name', read_only=True)
 #   test_title = serializers.CharField(source='test.title', read_only=True)

 #   class Meta:
 #       model = Candidate_Test
 #       # We only need the IDs to create the link, but we'll return more details
 #       fields = ['id', 'candidate', 'test', 'status', 'candidate_name', 'test_title']
 #       read_only_fields = ['id', 'status', 'candidate_name', 'test_title']
# --- NEW: A small serializer just for showing candidate details ---

class NestedCandidateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True, allow_null=True)

    class Meta:
        model = Candidate
        fields = ['name', 'email', 'phone']


# --- THIS IS THE CORRECTED ASSIGNMENT SERIALIZER ---
class TestAssignmentSerializer(serializers.ModelSerializer):
    # This now uses our new nested serializer to show full candidate details
    candidate = NestedCandidateSerializer(read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)

    class Meta:
        model = Candidate_Test
        # We define the fields we want in our final API response
        fields = ['id', 'candidate', 'test', 'status', 'test_title']
        read_only_fields = fields # Make all fields read-only for the list view
