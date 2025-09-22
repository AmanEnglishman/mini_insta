from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, CommentCreateSerializer
from .permissions import IsAuthorOrReadOnly
from users.serializers import UserSerializer


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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Лайк/анлайк поста"""
        post = self.get_object()
        user = request.user
        
        if user in post.likes.all():
            post.likes.remove(user)
            message = "Лайк убран"
        else:
            post.likes.add(user)
            message = "Пост лайкнут"
            
        return Response({
            'message': message,
            'likes_count': post.likes.count(),
            'is_liked': user in post.likes.all()
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def likes(self, request, pk=None):
        """Список пользователей, лайкнувших пост"""
        post = self.get_object()
        likes = post.likes.all()
        serializer = UserSerializer(likes, many=True)
        return Response({
            'likes_count': likes.count(),
            'users': serializer.data
        })


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


class TrendingPostsView(generics.ListAPIView):
    """
    Популярные посты:
    - GET /api/posts/trending/
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.annotate(
            likes_count=Count("likes")
        ).order_by("-likes_count", "-created_at")


class PostSearchView(generics.ListAPIView):
    """
    Поиск постов:
    - GET /api/posts/search/?q=query
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Post.objects.filter(
                caption__icontains=query
            ).select_related("author").prefetch_related("likes").order_by("-created_at")
        return Post.objects.none()


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Список и создание комментариев для поста:
    - GET /api/posts/<post_id>/comments/
    - POST /api/posts/<post_id>/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(
            post_id=post_id, 
            parent=None
        ).select_related('author').prefetch_related('replies')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление комментария:
    - GET /api/comments/<id>/
    - PUT/PATCH /api/comments/<id>/
    - DELETE /api/comments/<id>/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('author', 'post')


class AdminHidePostView(APIView):
    """
    Скрытие поста (только для админов):
    - POST /posts/admin/hide/<post_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        if not request.user.is_staff:
            return Response(
                {'error': 'Недостаточно прав'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        post = get_object_or_404(Post, id=post_id)
        post.delete()  # В реальном приложении лучше добавить поле is_hidden
        
        return Response({'message': f'Пост {post_id} скрыт'})


class AdminPostListView(generics.ListAPIView):
    """
    Список всех постов (только для админов):
    - GET /posts/admin/list/
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Post.objects.none()
        return Post.objects.all().select_related("author").prefetch_related("likes").order_by("-created_at")


class AdminCommentListView(generics.ListAPIView):
    """
    Список всех комментариев (только для админов):
    - GET /posts/admin/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Comment.objects.none()
        return Comment.objects.all().select_related('author', 'post').order_by('-created_at')
