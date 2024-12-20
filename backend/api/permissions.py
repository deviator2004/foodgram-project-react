from rest_framework import permissions


class IsStaffAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )


class IsAythForMe(permissions.BasePermission):
    def has_permission(self, request, view):
        if '/me/' in request.path:
            return request.user.is_authenticated
        return True
