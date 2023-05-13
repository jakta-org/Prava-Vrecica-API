from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .settings import *
from .models import Feedback
from .serializers import *
from accounts.decorators import *
from .decorators import *
from django.utils.decorators import method_decorator

class FeedbackView(APIView):
    @method_decorator(require_user_authenticated)
    def post(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CreateFeedbackSerializer(data=data)

        if serializer.is_valid():
            feedback = serializer.save(user=request.user)
            serializer = FeedbackRespondSerializer(feedback)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(require_user_authenticated)
    @method_decorator(admin_required)
    def get(self, request, format=None):
        serializer = FeedbackOptionsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        num = serializer.validated_data.get('num')
        since = serializer.validated_data.get('since')
        all = serializer.validated_data.get('all')

        if all is True:
            feedback = Feedback.objects.all()
        elif num is not None and since is not None:
            feedback = Feedback.objects.filter(upload_date__gte=since)[:num]
        elif num is not None:
            feedback = Feedback.objects.all()[:num]
        elif since is not None:
            feedback = Feedback.objects.filter(upload_date__gte=since)
        else:
            feedback = Feedback.objects.all()

        serializer = GetFeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(require_user_authenticated)
    @method_decorator(admin_required)
    @method_decorator(temporary_disabled)
    def delete(self, request, format=None):
        serializer = FeedbackOptionsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        num = serializer.validated_data.get('num')
        since = serializer.validated_data.get('since')
        all = serializer.validated_data.get('all')

        if all is True:
            feedback = Feedback.objects.all()
        elif num is not None and since is not None:
            feedback = Feedback.objects.filter(upload_date__gte=since)[:num]
        elif num is not None:
            feedback = Feedback.objects.all()[:num]
        elif since is not None:
            feedback = Feedback.objects.filter(upload_date__gte=since)
        else:
            feedback = Feedback.objects.all()[:set.DEFAULT_RETURN_FEEDBACK_NUM]

        feedback.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class name is not representative enough
class FeedbackDetailsView(APIView):
    @method_decorator(require_user_authenticated)
    @method_decorator(admin_required)
    @method_decorator(validate_feedback_param)
    def get(self, request, feedback_param, format=None):
        serializer = GetFeedbackSerializer(feedback_param)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(require_user_authenticated)
    @method_decorator(admin_required)
    @method_decorator(validate_feedback_param)
    def delete(self, request, feedback_param, format=None):
        feedback_param.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)