from rest_framework import generics, permissions
from .models import Test, Section, Question, Option
from .serializers import TestSerializer, SectionSerializer, QuestionSerializer, OptionSerializer
import json
from django.http import JsonResponse
from django.conf import settings

class CreateTestView(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ListTestView(generics.ListAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

def fetch_section_questions(request, section_id):
    with open(settings.BASE_DIR / 'test_creation' / 'test_questions.json') as f:
        data = json.load(f)

    for section in data:
        if section.get("section_id") == section_id:
            return JsonResponse(section, safe=False)

    return JsonResponse({'error': 'Section not found'}, status=404)