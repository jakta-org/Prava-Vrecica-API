from rest_framework import serializers
from .models import User, EntranceKey, Group, UserGroup
from django.utils import timezone
from django.db.models import Q

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'username', 'first_name', 'last_name', 'password', 'phone_number')

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'username', 'first_name', 'last_name', 'phone_number', 'score')

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
        model = UserGroup
        fields = ['group']

class GetGroupMembersSerializer(serializers.ModelSerializer):
    group_score = serializers.CharField(source='score')
    user = GetUserSerializer()

    class Meta:
        model = UserGroup
        fields = ['user', 'group_score']

# for updating user data in group
class UpdateUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ['score', 'is_moderator']

# serialize score as integer
class ScoreSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField()
    class Meta:
        fields = ['score']