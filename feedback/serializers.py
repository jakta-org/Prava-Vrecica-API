from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    image = serializers.CharField(required=True, max_length=100)
    user_id = serializers.CharField(required=False, max_length=100, default="")
    message = serializers.CharField(required=False, max_length=1000, default="")
    date = serializers.DateTimeField(required=True)
    is_correct = serializers.BooleanField(required=True)

    def create(self, validated_data):
        return Feedback.objects.create(**validated_data)
