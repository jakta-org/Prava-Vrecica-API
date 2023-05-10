from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.authentication import CustomTokenAuthentication

from django.contrib.auth.decorators import login_required
from .models import Feedback
from .serializers import FeedbackSerializer, FeedbackRespondSerializer

from accounts.decorators import *

from django.utils.decorators import method_decorator

class FeedbackView(APIView):
    @method_decorator(require_user_authenticated)
    def post(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = FeedbackSerializer(data=data)

        if serializer.is_valid():
            #serializer.create(serializer.validated_data)
            feedback = serializer.save(user=request.user)
            serializer = FeedbackRespondSerializer(feedback)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(require_user_authenticated)
    def get(self, request, format=None):
        num = request.GET.get('num', None)
        if num is not None:
            feedback = Feedback.objects.filter(id__lte=num).order_by('-id')[:10]
        else:
            feedback = Feedback.objects.all()
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)