from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("registro/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("vehiculos/nuevo/", views.vehicle_create, name="vehicle_create"),
    path("vigencias/nueva/", views.vigencia_create, name="vigencia_create"),
    path("vigencias/<int:pk>/renove/", views.vigencia_mark_renewed, name="vigencia_mark_renewed"),


    path("accounts/", include("django.contrib.auth.urls")),
]
