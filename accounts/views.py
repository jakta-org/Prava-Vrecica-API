from django.http import HttpRequest
from .models import EntranceKey, User, Token, Group
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .permissions import *
from .decorators import *
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator

class UserViews(APIView):
    @method_decorator(validate_entrence_key)
    def post(self, request, format=None):
        data = request.data.copy()
        entrance_code = data.get('entrance_code')
        data.pop('entrance_code', None)

        serializer = CreateUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(**serializer.validated_data)
        token = Token.objects.create(user=user)

        if entrance_code:
            key = EntranceKey.objects.get(code=entrance_code)
            if key.uses_left != None:
                key.uses_left -= 1
                key.save()

            if key.group_id != None:
                group = Group.objects.get(id=key.group_id)
                UserGroup.objects.create(group=group, user=user, is_moderator=False).save()

        return Response({'token': token.token}, status=status.HTTP_201_CREATED)
            
    
    @method_decorator(admin_required)
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = GetUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            serializer = GetUserSerializer(user)
            return Response({'token': token.token, 'user': serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_entrance_key(request):
    serializer = CreateEntranceKeySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = {'entrance_code': serializer.data['code'],
                'success': 'Entrance Key Created'}
        return Response(data=data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsView(APIView):
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def get(self, request, user_param, format=None):
        serializer = GetUserSerializer(user_param)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def put(self, request, user_param, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        user = User.objects.get(id=id)
        serializer = CreateUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def delete(self, request, user_param, format=None):
        user_param.is_active = False
        user_param.save()
        return Response({"message":"User deleted"}, status=status.HTTP_204_NO_CONTENT)

class UserScoreViews(APIView):
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def get(self, request, user_param, format=None):
        return Response({"score":user_param.score}, status=status.HTTP_200_OK)
    
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def patch(self, request, user_param, format=None):
        serializer = UserScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_param.score += serializer.validated_data['score']
        user_param.save()
        return Response({"score":user_param.score}, status=status.HTTP_200_OK)

    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def put(self, request, user_param, format=None):
        serializer = UserScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_param.score = serializer.validated_data['score']
        user_param.save()
        return Response({"score":user_param.score}, status=status.HTTP_200_OK)

class UserMetaDataViews(APIView):
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def get(self, request, user_param, format=None):
        return Response(user_param.meta_data, status=status.HTTP_200_OK)

    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def post(self, request, user_param, format=None):
        user_param.meta_data = request.data
        user_param.save()
        return Response(user_param.meta_data, status=status.HTTP_200_OK)
    
    @method_decorator(validate_user_param)
    @method_decorator(require_user_owner)
    def put(self, request, user_param, format=None):
        user_param.meta_data = request.data
        user_param.save()
        return Response(user_param.meta_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@require_user_authenticated
def create_group(request):
    serializer = CreateGroupSerializer(data=request.data)
    if serializer.is_valid():
        group = serializer.save()

        UserGroup.objects.create(group=group, user=request.user, is_moderator=True)
        data = {'group_id': group.id,
                'success': 'Group Created, user is moderator'}
        return Response(data=data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupViews(APIView):
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    def get(self, request, group_param, format=None):
        serializer = GetGroupSerializer(group_param)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    @method_decorator(require_user_moderator)
    def put(self, request, group_param, format=None):
        serializer = UpdateGroupSerializer(group_param, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Group updated'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    @method_decorator(require_user_moderator)
    def delete(self, request, group_param, format=None):
        group_param.is_active = False
        group_param.save()
        return Response({"message":"Group deleted"}, status=status.HTTP_204_NO_CONTENT)
    
class UserGroupViews(APIView):
    @method_decorator(validate_user_param)
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_owner)
    def post(self, request, user_param, group_param, format=None):
        user_group = UserGroup.objects.create(user=user_param, group=group_param)
        return Response({"message":"User added to group"}, status=status.HTTP_200_OK)
    
    @method_decorator(validate_user_param)
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    @method_decorator(require_user_owner)
    def delete(self, request, user_param, group_param, format=None):
        user_group = UserGroup.objects.get(user=user_param, group=group_param)
        user_group.delete()
        return Response({"message":"User removed from group"}, status=status.HTTP_204_NO_CONTENT)
    
    @method_decorator(validate_user_param)
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    @method_decorator(require_user_owner)
    def put(self, request, user_param, group_param, format=None):
        user_group = UserGroup.objects.get(user=user_param, group=group_param)
        serializer = UpdateUserGroupSerializer(user_group, data=request.data)
        serializer.save()
        return Response({"message":"User group data updated"}, status=status.HTTP_200_OK)
    
    @method_decorator(validate_user_param)
    @method_decorator(validate_group_param)
    @method_decorator(require_user_authenticated)
    @method_decorator(require_user_member)
    @method_decorator(require_user_owner)
    def patch(self, request, user_param, group_param, format=None):
        user_group = UserGroup.objects.get(user=user_param, group=group_param)
        serializer = GroupScoreSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_group.score = user_group.score + serializer.validated_data['score']
            user_group.save()
            return Response({"message":"User group data updated"}, status=status.HTTP_200_OK)
    

    
@api_view(['GET'])
@validate_group_param
@require_user_authenticated
@require_user_member
def get_group_members(request, group_param):
    users = UserGroup.objects.filter(group=group_param)
    serializer = GetGroupMembersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@require_user_authenticated
@validate_user_param
@require_user_owner
def get_user_groups(request, user_param):
    groups = UserGroup.objects.filter(user=user_param)
    serializer = GetUserGroupsSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
