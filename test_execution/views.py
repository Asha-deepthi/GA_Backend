from django.shortcuts import render
from rest_framework import generics
from .models import BasicDetails
from .serializers import BasicDetailsSerializer

class BasicDetailsCreateView(generics.CreateAPIView):
    queryset = BasicDetails.objects.all()
    serializer_class = BasicDetailsSerializer
