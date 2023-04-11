from rest_framework import serializers
from .models import User, EntranceKey
from django.utils import timezone
from django.db.models import Q

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email', 'username', 'first_name', 'last_name', 'password', 'phone_number')

class NewKeyUserSerializer(serializers.ModelSerializer):
    entrance_code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'phone_number', 'entrance_code')

    # validate entrance_code
    def validate_entrance_code(self, value):
        keys = EntranceKey.objects.filter(code=value)
        if not keys.exists():
            raise serializers.ValidationError('Invalid entrance code')
        
        key = keys.filter(code=value).filter(
            (Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())) &
            (Q(uses_left__isnull=True) | Q(uses_left__gt=0))
        ).first()

        #     expires_at is None or key.expires_at > datetime.now()) and
        #     (key.uses_left is None or key.uses_left > 0)
        # ).first()

        if key is None:
            raise serializers.ValidationError('Entrance Code Expired')
        
        if key.uses_left != None:
            key.uses_left -= 1
            key.save()
        return value


class EntranceKeySerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, read_only=True)

    class Meta:
        model = EntranceKey
        fields = ['group_id', 'expires_at', 'uses_left', 'code']