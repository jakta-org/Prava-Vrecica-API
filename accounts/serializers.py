from rest_framework import serializers
from .models import User, EntranceKey, Group
from django.utils import timezone
from django.db.models import Q

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'username', 'first_name', 'last_name', 'password', 'phone_number')

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'username', 'first_name', 'last_name', 'phone_number')

class CreateEntranceKeySerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, read_only=True)

    class Meta:
        model = EntranceKey
        fields = ['group_id', 'expires_at', 'uses_left', 'code']

class ParseEntranceKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceKey
        fields = ['code']

class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['type', 'meta_data', 'settings']

class GetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'type', 'meta_data', 'settings']

class UpdateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['type', 'meta_data', 'settings']

class GetUserGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id']

class GetGroupMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']