from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager
from . import settings as set
import string, random
from datetime import timedelta

class Token(models.Model):
    token = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=set.TOKEN_EXPIRATION_TIME)

        return super().save(*args, **kwargs)
    
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    google_id = models.CharField(max_length=100, blank=True)
    apple_id = models.CharField(max_length=100, blank=True)
    meta_data = models.JSONField(blank=True, null=True)
    score = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name


class EntranceKey(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6, blank=False, null=False)
    group_id = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    uses_left = models.IntegerField(default=None, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.code:
            characters = string.ascii_uppercase + string.digits
            self.code = ''.join(random.choices(characters, k=6))
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.code}'


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=30, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    settings = models.JSONField(blank=True, null=True)
    meta_data = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.id}'


class UserGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_moderator = models.BooleanField(default=False)
    meta_data = models.JSONField(blank=True, null=True)
    

