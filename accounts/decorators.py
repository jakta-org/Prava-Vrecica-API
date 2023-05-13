from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from .models import User, UserGroup, Group, EntranceKey
from django.utils import timezone

def validate_user_param(view_func):
    """
    Decorator to validate user in url parameter. Adds user_param object in kwargs. Removes user_id from kwargs.
    """
    def wrapped_view(request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs.get('user_id'))
        except User.DoesNotExist:
            return HttpResponseNotFound('The user does not exist.')
        if not user.is_active: 
            return HttpResponseForbidden("User is not active")
        kwargs['user_param'] = user
        kwargs.pop('user_id', None)
        return view_func(request, *args, **kwargs)
    return wrapped_view

def require_user_owner(view_func):
    """
    Decorator to require that the user is the owner of the requested resource.
    """
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated is False:
            return HttpResponse("Authentication failed, provide token", status=401)
        
        if kwargs['user_param'].id != request.user.id:
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

def validate_group_param(view_func):
    """
    Decorator to validate group in url parameter. Adds group_param object in kwargs. Removes group_id from kwargs.
    """
    def wrapped_view(request, *args, **kwargs):
        try:
            group = Group.objects.get(id=kwargs.get('group_id'))
        except Group.DoesNotExist:
            return HttpResponseNotFound('The group does not exist.')
        if not group.is_active: 
            return HttpResponseForbidden("Group is not active")
        kwargs['group_param'] = group
        kwargs.pop('group_id', None)
        return view_func(request, *args, **kwargs)
    return wrapped_view 

def require_user_member(view_func):
    """
    Decorator to require that the user is member.
    """
    def wrapped_view(request, *args, **kwargs):
        if not UserGroup.objects.filter(user=request.user, group=kwargs.get('group_param')).exists():
            return HttpResponseForbidden("Member access required")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view

def require_user_moderator(view_func):
    """
    Decorator to require that the user is moderator.
    """
    def wrapped_view(request, *args, **kwargs):
        if not UserGroup.objects.filter(user=request.user, group=kwargs.get('group_param'), is_moderator=True).exists():
            return HttpResponseForbidden("Moderator access required")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view

def validate_entrence_key(view_func):
    """
    Decorator to validate entrence key in url parameter. Adds entrence_key_param object in kwargs. Removes entrence_key_id from kwargs.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.data.get('entrance_code'):
            return HttpResponseForbidden("Entrance Key is not provided")
        try:
            entrence_key = EntranceKey.objects.get(code=request.data.get('entrance_code'))
        except EntranceKey.DoesNotExist:
            return HttpResponseNotFound('Entrence key does not exist.')
        
        if not entrence_key.is_active: 
            return HttpResponseForbidden("Entrance Key is not active")
        
        if entrence_key.expires_at != None and entrence_key.expires_at < timezone.now():
            return HttpResponseForbidden("Entrance Key expired")
        
        if entrence_key.uses_left != None and entrence_key.uses_left <= 0:
            return HttpResponseForbidden("Entrance Key is out of uses")
    
        return view_func(request, *args, **kwargs)
    return wrapped_view

def temporary_disabled(view_func):
    """
    Decorator to temporary disable view.
    """
    def wrapped_view(request, *args, **kwargs):
        return HttpResponseForbidden("View temporary disabled")
    return wrapped_view