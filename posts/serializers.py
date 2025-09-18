from rest_framework import serializers
from .models import Post
from users.models import User


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author', 'image', 'caption', 'likes_count', 'created_at')

    def get_likes_count(self, obj):
        return obj.likes.count()