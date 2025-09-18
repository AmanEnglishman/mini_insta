from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, FeedView

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', FeedView.as_view(), name='feed'),
]
