from rest_framework import permissions

class IsUserOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        return True
    
    def has_object_permission(self, request, view, obj) -> bool:
        # Write permissions are only allowed to the owner of the snippet.
        return obj == request.user
    
class IsUserActive(permissions.BasePermission):
    """
    Custom permission to only allow active users to view content.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_active