from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Vehicle, Vigencia
from datetime import date, timedelta

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_landing_page_anonymous(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/landing.html')
    
    def test_landing_page_authenticated_redirect(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('landing'), follow=True)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("dashboard")}')
    
    def test_dashboard_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

class VehicleViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_vehicle_create_get(self):
        response = self.client.get(reverse('vehicle_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/vehicle_form.html')
    
    def test_vehicle_create_post_valid(self):
        data = {
            'alias': 'Mi Carro Test',
            'plate': 'ABC123'
        }
        response = self.client.post(reverse('vehicle_create'), data, follow=True)
        
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Vehicle.objects.filter(alias='Mi Carro Test').exists())
    
    def test_vehicle_create_post_invalid(self):
        data = {
            'alias': '',  # Nombre vacío
            'plate': 'ABC123'
        }
        response = self.client.post(reverse('vehicle_create'), data)
        
        self.assertEqual(response.status_code, 200)  # No redirecciona
        self.assertContains(response, "Por favor ingresa un nombre para el vehículo")