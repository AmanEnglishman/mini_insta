from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password

from .models import Profile, User
from .serializers import ProfileSerializer, UserSerializer, RegisterSerializer, LoginSerializer
from posts.serializers import PostSerializer
from posts.models import Post


class MyProfileAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPI(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        """Создаем пользователя и автоматически входим в систему"""
        user = serializer.save()
        login(self.request, user)
        
    def create(self, request, *args, **kwargs):
        """Переопределяем create для возврата данных профиля после регистрации"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Получаем созданный профиль
        profile = serializer.instance.profile
        profile_serializer = ProfileSerializer(profile)
        
        return Response({
            'message': 'Регистрация успешна',
            'profile': profile_serializer.data
        }, status=status.HTTP_201_CREATED)


class LoginAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.data['email'],
            password=serializer.data['password']
        )

        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class UserProfileAPI(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer
    lookup_field = 'username'
    queryset = User.objects.all()

    def get_object(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return user.profile


class FollowToggleView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)

        if target_user == request.user:
            return Response({'message': 'Нельзя подписываться на себя'}, status=status.HTTP_400_BAD_REQUEST)

        target_profile = target_user.profile
        current_profile = request.user.profile

        if target_profile in current_profile.following.all():
            current_profile.following.remove(target_profile)
            return Response({'message': "Вы отписались"})
        else:
            current_profile.following.add(target_profile)
            return Response({"message": "Вы подписались"})


class UserFollowersView(generics.ListAPIView):
    """
    Список подписчиков пользователя:
    - GET /users/<username>/followers/
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        followers_profiles = user.profile.followers.all()
        return [profile.user for profile in followers_profiles]


class UserFollowingView(generics.ListAPIView):
    """
    Список подписок пользователя:
    - GET /users/<username>/following/
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        following_profiles = user.profile.following.all()
        return [profile.user for profile in following_profiles]


class UserPostsView(generics.ListAPIView):
    """
    Посты пользователя:
    - GET /users/<username>/posts/
    """
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).select_related('author').prefetch_related('likes')


class UserSearchView(generics.ListAPIView):
    """
    Поиск пользователей:
    - GET /users/search/?q=query
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return User.objects.filter(
                Q(username__icontains=query) | 
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query)
            )
        return User.objects.none()


class UserStatsView(APIView):
    """
    Статистика пользователя:
    - GET /users/me/stats/
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = user.profile
        
        stats = {
            'posts_count': Post.objects.filter(author=user).count(),
            'followers_count': profile.followers.count(),
            'following_count': profile.following.count(),
            'total_likes_received': Post.objects.filter(author=user).aggregate(
                total_likes=Count('likes')
            )['total_likes'] or 0,
        }
        
        return Response(stats)


class ChangePasswordView(APIView):
    """
    Смена пароля:
    - POST /users/change-password/
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Требуются old_password и new_password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Неверный старый пароль'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password, user=request.user)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Пароль успешно изменен'})


class DeleteAccountView(APIView):
    """
    Удаление аккаунта:
    - DELETE /users/delete-account/
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'Требуется пароль для подтверждения'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(password):
            return Response(
                {'error': 'Неверный пароль'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.delete()
        return Response({'message': 'Аккаунт успешно удален'})


class AdminBanUserView(APIView):
    """
    Блокировка пользователя (только для админов):
    - POST /users/admin/ban/<user_id>/
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        if not request.user.is_staff:
            return Response(
                {'error': 'Недостаточно прав'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()
        
        return Response({'message': f'Пользователь {user.username} заблокирован'})


class AdminUnbanUserView(APIView):
    """
    Разблокировка пользователя (только для админов):
    - POST /users/admin/unban/<user_id>/
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        if not request.user.is_staff:
            return Response(
                {'error': 'Недостаточно прав'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()
        
        return Response({'message': f'Пользователь {user.username} разблокирован'})


class AdminUserListView(generics.ListAPIView):
    """
    Список всех пользователей (только для админов):
    - GET /users/admin/list/
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.none()
        return User.objects.all().order_by('-date_joined')

