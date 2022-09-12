from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (
                request.user.is_superuser
                or obj.author == request.user
                or request.method == 'POST'
        ):
            return True
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrReadOnlyPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
