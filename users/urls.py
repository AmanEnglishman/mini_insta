from django.urls import path

from .views import MyProfileAPI, LoginAPI, RegisterAPI

urlpatterns = [
    path('profile/', MyProfileAPI.as_view(), name='profile'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('register/', RegisterAPI.as_view(), name='register'),
]