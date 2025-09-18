from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from django.db.models import Count
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    CRUD для постов:
    - POST /api/posts/
    - GET /api/posts/
    - GET /api/posts/<id>/
    - PUT/PATCH/DELETE /api/posts/<id>/
    """
    queryset = Post.objects.all().select_related("author").prefetch_related("likes")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        sort_by = self.request.query_params.get("sort")

        if sort_by == "popular":
            return qs.annotate(likes_count=Count("likes")).order_by("-likes_count", "-created_at")
        return qs.order_by("-created_at")


class FeedView(generics.ListAPIView):
    """
    Лента подписок:
    - GET /api/feed/
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_profiles = user.profile.following.all()
        following_users = [p.user for p in following_profiles]

        return Post.objects.filter(author__in=following_users).order_by("-created_at")
