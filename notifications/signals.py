from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Notification
from posts.models import Post, Comment

User = get_user_model()


@receiver(m2m_changed, sender=Post.likes.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    """Создание уведомления при лайке поста"""
    if action == 'post_add':
        for user_id in pk_set:
            user = User.objects.get(id=user_id)
            if user != instance.author:  # Не уведомляем автора о своем лайке
                Notification.objects.create(
                    recipient=instance.author,
                    sender=user,
                    notification_type='like',
                    message=f'{user.username} лайкнул ваш пост',
                    post=instance
                )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Создание уведомления при комментарии"""
    if created and instance.author != instance.post.author:
        Notification.objects.create(
            recipient=instance.post.author,
            sender=instance.author,
            notification_type='comment',
            message=f'{instance.author.username} прокомментировал ваш пост',
            post=instance.post,
            comment=instance
        )


# Временно отключено - нужно исправить сигнал
# @receiver(m2m_changed, sender='users.Profile.following')
# def create_follow_notification(sender, instance, action, pk_set, **kwargs):
#     """Создание уведомления при подписке"""
#     if action == 'post_add':
#         for profile_id in pk_set:
#             from users.models import Profile
#             profile = Profile.objects.get(id=profile_id)
#             if profile.user != instance.user:  # Не уведомляем о подписке на себя
#                 Notification.objects.create(
#                     recipient=profile.user,
#                     sender=instance.user,
#                     notification_type='follow',
#                     message=f'{instance.user.username} подписался на вас'
#                 )
