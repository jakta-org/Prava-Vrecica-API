from django.http import HttpRequest
from .models import User, Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer
from .serializers import EntranceKeySerializer, NewKeyUserSerializer
from rest_framework.decorators import api_view

class UserViews(APIView):
    def post(self, request, format=None):
        entrance_code = request.data.get('entrance_code')

        if entrance_code:
            serializer = NewKeyUserSerializer(data=request.data)
        else:
            serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data.pop('entrance_code', None)
            user = User.objects.create_user(**serializer.validated_data)
            if user:
                token = Token.objects.create(user=user)
                return Response({'token': token.token}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TokenViews(APIView):
    def post(self, request: HttpRequest, format=None):
        print(request.content_type)
        mail = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        if not mail and not username or not password:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if mail:
            user = User.objects.get(email=mail)
        elif username:
            user = User.objects.get(username=username)

        if user and user.check_password(password):
            token = Token.objects.get(user=user)
            return Response({'token': token.token}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_entrance_key(request):
    serializer = EntranceKeySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = {'entrance_code': serializer.data['code'],
                'success': 'Entrance Key Created'}
        return Response(data=data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)