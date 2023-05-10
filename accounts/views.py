from django.http import HttpRequest
from .models import EntranceKey, User, Token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .authentication import CustomTokenAuthentication
from rest_framework.decorators import authentication_classes
from .serializers import CustomUserSerializer, GetUserSerializer
from .serializers import EntranceKeySerializer, NewKeyUserSerializer
from rest_framework.decorators import api_view
from .permissions import *
from .decorators import *
from django.utils.decorators import method_decorator

class UserViews(APIView):
    def post(self, request, format=None):
        entrance_code = request.data.get('entrance_code')

        if entrance_code:
            serializer = NewKeyUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data.pop('entrance_code', None)
                user = User.objects.create_user(**serializer.validated_data)
                if user:
                    key = EntranceKey.objects.get(code=entrance_code)
                    if key.uses_left != None:
                        key.uses_left -= 1
                        key.save()

                    token = Token.objects.create(user=user)
                    return Response({'token': token.token}, status=status.HTTP_201_CREATED)
        else:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data.pop('entrance_code', None)
                user = User.objects.create_user(**serializer.validated_data)
                if user:
                    token = Token.objects.create(user=user)
                    return Response({'token': token.token}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    @method_decorator(admin_required)
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = GetUserSerializer(users, many=True)
        return Response(serializer.data)

class TokenViews(APIView):
    # access token
    def post(self, request: HttpRequest, format=None):
        mail = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        if not mail and not username or not password:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if mail:
            user = User.objects.filter(email=mail).first()
        elif username:
            user = User.objects.filter(username=username).first()
            
        if user and user.check_password(password):
            token = Token.objects.create(user=user)
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

class UserDetailsView(APIView):
    @method_decorator(require_user_owner)
    def get(self, request, id, format=None):
        user = request.user
        serializer = GetUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(require_user_owner)
    def put(self, request, id, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        user = User.objects.get(id=id)
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(require_user_owner)
    def delete(self, request, id, format=None):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message":"User deleted"}, status=status.HTTP_204_NO_CONTENT)

class UserMetaDataViews(APIView):
    @method_decorator(require_user_owner)
    def get(self, request, id, format=None):
        user = request.user
        return Response(user.meta_data, status=status.HTTP_200_OK)

    @method_decorator(require_user_owner)
    def post(self, request, id, format=None):
        user = request.user
        user.meta_data = request.data
        user.save()
        return Response(user.meta_data, status=status.HTTP_200_OK)
    
    @method_decorator(require_user_owner)
    def put(self, request, id, format=None):
        user = request.user
        user.meta_data = request.data
        user.save()
        return Response(user.meta_data, status=status.HTTP_200_OK)
    
