from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("vehiculos/nuevo/", views.vehicle_create, name="vehicle_create"),
    path("vigencias/nueva/", views.vigencia_create, name="vigencia_create"),
    path("vigencias/<int:pk>/renove/", views.vigencia_mark_renewed, name="vigencia_mark_renewed"),

    path("pro/solicitar/", views.pro_request, name="pro_request"),
    path("accounts/", include("allauth.urls")),
]
