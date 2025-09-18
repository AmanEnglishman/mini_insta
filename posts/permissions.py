from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Только автор может редактировать или удалять свой пост.
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS доступны всем
        if request.method in SAFE_METHODS:
            return True
        # редактировать/удалять может только автор
        return obj.author == request.user
