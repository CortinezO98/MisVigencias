from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('payment/create/', views.create_payment, name='create_payment'),
    path('payu/webhook/', views.payu_webhook, name='payu_webhook'),
    path('subscription/upgrade/', views.upgrade_subscription, name='upgrade_subscription'),
]