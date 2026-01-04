from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Profile, Vehicle, Vigencia
from billing.models import Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class VigenciaSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        source='vehicle',
        write_only=True
    )
    
    class Meta:
        model = Vigencia
        fields = '__all__'
        read_only_fields = ('created_at', 'last_notified_at')
    
    def validate(self, data):
        # Validar que el vehículo pertenezca al usuario
        request = self.context.get('request')
        if request and data.get('vehicle'):
            if data['vehicle'].owner != request.user:
                raise serializers.ValidationError(
                    "El vehículo no pertenece al usuario"
                )
        return data

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')