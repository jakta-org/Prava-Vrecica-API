from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

class Token(models.Model):
    token = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
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
            self.code = uuid.uuid4().hex[:6]
        return super().save(*args, **kwargs)

class UserGroup(models.Model):
    pass