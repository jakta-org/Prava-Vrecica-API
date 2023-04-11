from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.forms import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, **fields):
        email = fields.get('email', None)
        password = fields.get('password', None)

        if not email:
            raise ValidationError('Users must have an email address')
        if not password:
            raise ValidationError('Users must have a password')
        
        fields['email'] = self.normalize_email(email)

        user = self.model.objects.create(**fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(**extra_fields)
    
