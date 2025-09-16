from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate, login, logout

from .models import Profile, User
from .serializers import ProfileSerializer, UserSerializer, RegisterSerializer, LoginSerializer


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

