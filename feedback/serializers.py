from rest_framework import serializers
from .models import Feedback
import base64
from django.core.files.base import ContentFile

class CreateFeedbackSerializer(serializers.ModelSerializer):
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
        feedback.image.name = file_name

        feedback.image.save(file_name, ContentFile(base64.b64decode(image_data)), save=True)
        return feedback
    
class FeedbackRespondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['message', 'is_trusted', 'user', 'id']

class FeedbackOptionsSerializer(serializers.Serializer):
    num = serializers.IntegerField(required=False)
    since = serializers.DateTimeField(required=False)
    all = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if attrs.get('num') is not None and attrs.get('all') is not None:
            raise serializers.ValidationError("Cannot specify both 'num' and 'all' parameters")
        if attrs.get('since') is not None and attrs.get('all') is not None:
            raise serializers.ValidationError("Cannot specify both 'since' and 'all' parameters")
        return super().validate(attrs)

class GetFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'message', 'is_trusted', 'user', 'objects_data', 'image']