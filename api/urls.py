from django.urls import path, include
from .views import HealthCheckView, APIVersionView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='api-health'),
    path('version/', APIVersionView.as_view(), name='api-version'),
    path('v1/', include('api.v1.urls')),
]
