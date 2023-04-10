from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback
from .serializers import FeedbackSerializer

class FeedbackView(APIView):
    def post(self, request, format=None):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        num = request.GET.get('num', None)
        if num is not None:
            feedback = Feedback.objects.filter(id__lte=num).order_by('-id')[:10]
        else:
            feedback = Feedback.objects.all()
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)