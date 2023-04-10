from django.shortcuts import render
from .models import User, Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer
from django.contrib.auth.hashers import make_password

class UserViews(APIView):
    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TokenViews(APIView):
    def post(self, request, format=None):
        mail = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        # print(username, Token.objects.all()[0].key)
        if mail and password:
            user = User.objects.filter(email=mail, password=password).first()
            if user:
                token = Token.objects.get(user=user)
                return Response({'token': token.token}, status=status.HTTP_200_OK)
            
        elif username and password:
            user = User.objects.get(username=username)
            
            if user:
                token = Token.objects.get(user=user)
                return Response({'token': token.token}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
