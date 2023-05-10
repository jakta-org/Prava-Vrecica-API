from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from .models import User

def require_user_owner(view_func):
    """
    Decorator to require that the user is the owner of the requested resource.
    """
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated is False:
            return HttpResponse("Token not provided", status=401)
        
        if User.objects.filter(id=kwargs.get('id')).exists() is False:
            return HttpResponseNotFound('The user does not exist.')
        
        if kwargs.get('id') != request.user.id:
            return HttpResponseForbidden('You do not have permission to access this resource.')
        return view_func(request, *args, **kwargs)
    return wrapped_view

def require_user_authenticated(view_func):
    """
    Decorator to require that the user is authenticated.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("Authentication failed, provide token", status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

def admin_required(view_func):
    """
    Decorator to require that the user is admin.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("Authentication failed, provide token", status=401)
        if not request.user.is_staff:
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return wrapped_view