from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Vehículos
    path("vehiculos/nuevo/", views.vehicle_create, name="vehicle_create"),
    path("vehiculos/<int:pk>/editar/", views.vehicle_edit, name="vehicle_edit"),
    path("vehiculos/<int:pk>/eliminar/", views.vehicle_delete, name="vehicle_delete"),
    
    # Vigencias
    path("vigencias/nueva/", views.vigencia_create, name="vigencia_create"),
    path("vigencias/<int:pk>/editar/", views.vigencia_edit, name="vigencia_edit"),
    path("vigencias/<int:pk>/eliminar/", views.vigencia_delete, name="vigencia_delete"),
    path("vigencias/<int:pk>/renove/", views.vigencia_mark_renewed, name="vigencia_mark_renewed"),
    
    path("perfil/", views.profile_settings, name="profile_settings"),
    
    # PRO
    path("pro/solicitar/", views.pro_request, name="pro_request"),
    path("accounts/", include("allauth.urls")),
]
