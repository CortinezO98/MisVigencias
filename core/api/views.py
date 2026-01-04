from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Profile, Vehicle, Vigencia
from billing.models import Subscription
from .serializers import (
    UserSerializer, ProfileSerializer, VehicleSerializer,
    VigenciaSerializer, SubscriptionSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.models import FCMToken

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class VigenciaViewSet(viewsets.ModelViewSet):
    serializer_class = VigenciaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Vigencia.objects.filter(vehicle__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        vigencia = self.get_object()
        vigencia.activo = False
        vigencia.save()
        return Response({'status': 'renewed'})
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Vigencias próximas a vencer (7 días)"""
        upcoming = self.get_queryset().filter(
            activo=True,
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=7)
        )
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Estadísticas
        vehicles = Vehicle.objects.filter(owner=user).count()
        active_vigencias = Vigencia.objects.filter(
            vehicle__owner=user,
            activo=True
        ).count()
        
        upcoming_vigencias = Vigencia.objects.filter(
            vehicle__owner=user,
            activo=True,
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=7)
        ).count()
        
        expired_vigencias = Vigencia.objects.filter(
            vehicle__owner=user,
            activo=True,
            fecha_vencimiento__lt=timezone.now().date()
        ).count()
        
        profile = Profile.objects.get(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(profile).data,
            'stats': {
                'vehicles': vehicles,
                'active_vigencias': active_vigencias,
                'upcoming_vigencias': upcoming_vigencias,
                'expired_vigencias': expired_vigencias,
            }
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_fcm_token(request):
    """Registrar/actualizar token FCM"""
    token = request.data.get('token')
    device_type = request.data.get('device_type', 'ANDROID')
    device_name = request.data.get('device_name', '')
    
    if not token:
        return Response({'error': 'Token requerido'}, status=400)
    
    # Actualizar o crear token
    fcm_token, created = FCMToken.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user,
            'device_type': device_type,
            'device_name': device_name,
            'is_active': True
        }
    )
    
    return Response({
        'status': 'registered',
        'created': created,
        'token_id': fcm_token.id
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unregister_fcm_token(request):
    """Desactivar token FCM"""
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token requerido'}, status=400)
    
    FCMToken.objects.filter(
        token=token,
        user=request.user
    ).update(is_active=False)
    
    return Response({'status': 'unregistered'})