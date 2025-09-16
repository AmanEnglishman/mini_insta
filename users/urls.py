from django.urls import path

from .views import MyProfileAPI, LoginAPI, RegisterAPI, UserProfileAPI, FollowToggleView

urlpatterns = [
    path('profile/', MyProfileAPI.as_view(), name='profile'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('<str:username>/', UserProfileAPI.as_view(), name='profile'),
    path('<str:username>/follow/', FollowToggleView.as_view(), name='follow-toggle')
]
