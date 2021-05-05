from rest_framework.permissions import BasePermission, SAFE_METHODS


ALLOWED = ["like", "dislike", "add_comment"]


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class CanReactToPost(BasePermission):
    def has_object_permission(self, request, view, obj):
        return view.action in ALLOWED