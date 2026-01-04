from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'vehicles', views.VehicleViewSet, basename='vehicle')
router.register(r'vigencias', views.VigenciaViewSet, basename='vigencia')
router.register(r'subscription', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardAPIView.as_view(), name='api_dashboard'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]