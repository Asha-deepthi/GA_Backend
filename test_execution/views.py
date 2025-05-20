from django.shortcuts import render
from rest_framework import generics
from .models import BasicDetails
from .serializers import BasicDetailsSerializer
from .models import DemoQuestion
from .serializers import DemoQuestionSerializer

class BasicDetailsCreateView(generics.CreateAPIView):
    queryset = BasicDetails.objects.all()
    serializer_class = BasicDetailsSerializer

class DemoQuestionListView(generics.ListAPIView):
    queryset = DemoQuestion.objects.all()
    serializer_class = DemoQuestionSerializer