from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    Список уведомлений пользователя:
    - GET /notifications/
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'post', 'comment')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали уведомления:
    - GET /notifications/<id>/
    - PATCH /notifications/<id>/ (отметить как прочитанное)
    - DELETE /notifications/<id>/
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Уведомление отмечено как прочитанное'})


class MarkAllReadView(APIView):
    """
    Отметить все уведомления как прочитанные:
    - POST /notifications/mark-all-read/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'message': 'Все уведомления отмечены как прочитанные'})


class UnreadCountView(APIView):
    """
    Количество непрочитанных уведомлений:
    - GET /notifications/unread-count/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})