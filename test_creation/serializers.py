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

class FullOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        # We only need the data to create a new quiz, not the old IDs.
        fields = ['text', 'is_correct', 'weightage']

class FullQuestionSerializer(serializers.ModelSerializer):
    # This is the important part: we nest the options inside the questions.
    # We use 'source="options"' because your model's related_name is 'options'.
    # We rename it to 'answers' to match your frontend `CreateQuestionsPage` logic.
    answers = FullOptionSerializer(many=True, source='options')

    class Meta:
        model = Question
        fields = [
            'type', 'text', 'allow_multiple', 'paragraph_content',
            'fib_answer', 'video_time', 'audio_time', 'answers'
        ]

class FullSectionSerializer(serializers.ModelSerializer):
    # Nest the questions inside the sections.
    questions = FullQuestionSerializer(many=True, read_only=True) # Use read_only=True

    # --- THIS IS THE FIX ---
    # We are manually defining fields to map the snake_case model fields
    # to the camelCase keys that the React frontend expects.

    # Map model field 'name' to output key 'sectionName'
    sectionName = serializers.CharField(source='name')
    # Map model field 'type' to output key 'sectionType'
    sectionType = serializers.CharField(source='type')
    # Map model field 'time_limit' to output key 'timeLimit'
    timeLimit = serializers.CharField(source='time_limit')
    # Map model field 'num_questions' to output key 'noOfQuestions'
    noOfQuestions = serializers.IntegerField(source='num_questions')
    # Map model field 'marks_per_question' to output key 'marksPerQuestion'
    marksPerQuestion = serializers.IntegerField(source='marks_per_question')
    # Map model field 'negative_marks' to output key 'negative_marks'
    negativeMarks = serializers.FloatField(source='negative_marks')
    # Map model field 'instructions' to output key 'sectionInstructions'
    sectionInstructions = serializers.CharField(source='instructions')
    
    class Meta:
        model = Section
        # Now, we list the NEW camelCase field names in the 'fields' list.
        # The 'source' attribute tells Django where to get the data from.
        fields = [
            'id','sectionName', 'sectionType', 'timeLimit', 'noOfQuestions',
            'marksPerQuestion', 'negativeMarks', 'sectionInstructions',
            'shuffle_questions', 'shuffle_answers', # These match already
            'questions'
        ]

class FullTestDetailSerializer(serializers.ModelSerializer):
    # Nest the sections using our new serializer.
    sections = FullSectionSerializer(many=True)
    
    # Map model fields to the keys your frontend state expects (e.g., in quizData.settings)
    # This avoids having to change the frontend structure.
    passingPercentage = serializers.IntegerField(source='passing_percentage', required=False)
    scoring = serializers.CharField(source='scoring_type', required=False)
    negativeMarking = serializers.CharField(source='negative_marking_type', required=False)
    backNavigation = serializers.BooleanField(source='allow_back_navigation', required=False)
    results = serializers.CharField(source='results_display_type', required=False)
    attempts = serializers.CharField(source='attempts_type', required=False)
    numberOfAttempts = serializers.IntegerField(source='number_of_attempts', required=False)

    class Meta:
        model = Test
        # This structure is designed to match your frontend's `quizData` state perfectly.
        fields = [
            # details
            'title', 'level', 'description', 'duration', 'tags',
            # settings
            'passingPercentage', 'scoring', 'negativeMarking',
            'backNavigation', 'results', 'attempts', 'numberOfAttempts',
            # sections
            'sections'
        ]