from rest_framework import permissions


class CurrentUserOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj == user:
            return True
        return user.is_staff
