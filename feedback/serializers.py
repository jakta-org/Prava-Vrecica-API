from rest_framework import serializers
from .models import Feedback
import base64

class FeedbackSerializer(serializers.ModelSerializer):
    image_data = serializers.SerializerMethodField()

    def get_image_data(self, obj):
        data = obj.image.read()
        return base64.b64encode(data).decode('utf-8')

    class Meta:
        model = Feedback
        fields = ['id', 'frames_data', 'image_data', 'user_id', 'message', 'upload_date', 'is_correct', 'detected_object_id', 'correct_object_id']
