from rest_framework import serializers
from .models import Feedback
import base64
from django.core.files.base import ContentFile

class FeedbackSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    file_name = serializers.CharField()

    class Meta:
        model = Feedback
        fields = ['objects_data', 'image', 'message', 'is_trusted', 'user','file_name']

    def create(self, validated_data):
        image_data = validated_data.pop('image')
        file_name = validated_data.pop('file_name')

        feedback = Feedback.objects.create(**validated_data)

        ext = file_name.split('.')[-1]
        file_name = str(feedback.id) + '.' + ext

        feedback.image.save(file_name, ContentFile(base64.b64decode(image_data)), save=True)
        return feedback
    
class FeedbackRespondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['message', 'is_trusted', 'user', 'id']