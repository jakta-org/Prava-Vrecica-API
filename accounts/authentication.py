from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Token
from django.utils import timezone

class CustomTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(token=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')
        
        if not token.is_active:
            raise AuthenticationFailed('Token inactive or deleted.')
        if token.expires_at is not None and token.expires_at < timezone.now():
            raise AuthenticationFailed('Token expired.')
        
        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')
        return (token.user, token)
    