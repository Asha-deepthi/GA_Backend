from rest_framework import serializers
from .models import BasicDetails

class BasicDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicDetails
        fields = '__all__'
