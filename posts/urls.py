from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, FeedView, TrendingPostsView, PostSearchView, 
    CommentListCreateView, CommentDetailView,
    AdminHidePostView, AdminPostListView, AdminCommentListView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', FeedView.as_view(), name='feed'),
    path('posts/trending/', TrendingPostsView.as_view(), name='trending-posts'),
    path('posts/search/', PostSearchView.as_view(), name='post-search'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='post-comments'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    # Административные функции
    path('admin/list/', AdminPostListView.as_view(), name='admin-post-list'),
    path('admin/hide/<int:post_id>/', AdminHidePostView.as_view(), name='admin-hide-post'),
    path('admin/comments/', AdminCommentListView.as_view(), name='admin-comment-list'),
]
