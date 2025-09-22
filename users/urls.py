from django.urls import path

from .views import (
    MyProfileAPI, LoginAPI, RegisterAPI, UserProfileAPI, FollowToggleView, LogoutAPI,
    UserFollowersView, UserFollowingView, UserPostsView, UserSearchView, 
    UserStatsView, ChangePasswordView, DeleteAccountView,
    AdminBanUserView, AdminUnbanUserView, AdminUserListView
)

urlpatterns = [
    path('profile/', MyProfileAPI.as_view(), name='profile'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('me/stats/', UserStatsView.as_view(), name='user-stats'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('<str:username>/', UserProfileAPI.as_view(), name='user-profile'),
    path('<str:username>/follow/', FollowToggleView.as_view(), name='follow-toggle'),
    path('<str:username>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('<str:username>/following/', UserFollowingView.as_view(), name='user-following'),
    path('<str:username>/posts/', UserPostsView.as_view(), name='user-posts'),
    # Административные функции
    path('admin/list/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/ban/<int:user_id>/', AdminBanUserView.as_view(), name='admin-ban-user'),
    path('admin/unban/<int:user_id>/', AdminUnbanUserView.as_view(), name='admin-unban-user'),
]
