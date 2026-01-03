from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Vehicle, Vigencia
from datetime import date, timedelta

class VehicleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_vehicle_creation(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            alias='Mi Carro Test',
            plate='ABC123'
        )
        self.assertEqual(vehicle.alias, 'Mi Carro Test')
        self.assertEqual(vehicle.plate, 'ABC123')
        self.assertEqual(vehicle.owner, self.user)
        self.assertTrue(isinstance(vehicle, Vehicle))
    
    def test_vehicle_str_with_plate(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            alias='Test Car',
            plate='XYZ789'
        )
        self.assertEqual(str(vehicle), 'Test Car (XYZ789)')
    
    def test_vehicle_str_without_plate(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            alias='Test Car'
        )
        self.assertEqual(str(vehicle), 'Test Car')

class VigenciaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            alias='Test Vehicle'
        )
    
    def test_vigencia_creation(self):
        future_date = date.today() + timedelta(days=30)
        vigencia = Vigencia.objects.create(
            vehicle=self.vehicle,
            tipo='SOAT',
            fecha_vencimiento=future_date,
            activo=True
        )
        
        self.assertEqual(vigencia.tipo, 'SOAT')
        self.assertEqual(vigencia.activo, True)
        self.assertEqual(vigencia.vehicle, self.vehicle)
    
    def test_days_left_calculation(self):
        future_date = date.today() + timedelta(days=10)
        vigencia = Vigencia.objects.create(
            vehicle=self.vehicle,
            tipo='TECNO',
            fecha_vencimiento=future_date,
            activo=True
        )
        
        self.assertEqual(vigencia.days_left(), 10)
    
    def test_expired_vigencia(self):
        past_date = date.today() - timedelta(days=5)
        vigencia = Vigencia.objects.create(
            vehicle=self.vehicle,
            tipo='SOAT',
            fecha_vencimiento=past_date,
            activo=True
        )
        
        self.assertEqual(vigencia.days_left(), -5)