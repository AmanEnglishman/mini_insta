from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class HealthCheckView(APIView):
    """
    Проверка состояния API:
    - GET /api/health/
    """
    permission_classes = []

    def get(self, request):
        return Response({
            'status': 'healthy',
            'version': '1.0.0',
            'django_version': settings.DJANGO_VERSION,
        })


class APIVersionView(APIView):
    """
    Информация о версии API:
    - GET /api/version/
    """
    permission_classes = []

    def get(self, request):
        return Response({
            'current_version': 'v1',
            'api_name': 'Mini Instagram API',
            'version': '1.0.0',
            'supported_versions': ['v1'],
        })
