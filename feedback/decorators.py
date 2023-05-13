from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback

def validate_feedback_param(view_func):
    def wrapper(request, feedback_param, *args, **kwargs):
        try:
            feedback = Feedback.objects.get(id=feedback_param)
        except Feedback.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        kwargs['feedback_param'] = feedback
        kwargs.pop('feedback_id', None)
        return view_func(request, feedback, *args, **kwargs)
    return wrapper
