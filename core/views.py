from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .validators import validar_placa_colombiana
from .forms import VigenciaFilterForm
from .forms import ProfileForm
from core.models import OfficialService

from .models import Vehicle, Vigencia, PlanChoices


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    # Obtener todos los vehículos del usuario
    vehicles = Vehicle.objects.filter(owner=request.user)
    
    # Inicializar queryset
    vigencias = Vigencia.objects.filter(
        vehicle__owner=request.user, 
        activo=True
    ).select_related('vehicle')
    
    # Formulario de filtros
    filter_form = VigenciaFilterForm(request.GET or None, user_vehicles=vehicles)
    # Obtener servicios oficiales activos
    official_services = OfficialService.objects.filter(is_active=True).order_by("sort_order", "title")
    # Aplicar filtros
    if filter_form.is_valid():
        tipo = filter_form.cleaned_data.get('tipo')
        estado = filter_form.cleaned_data.get('estado')
        vehicle_id = filter_form.cleaned_data.get('vehicle')
        
        hoy = timezone.localdate()
        
        if tipo:
            vigencias = vigencias.filter(tipo=tipo)
        
        if estado:
            if estado == 'vencido':
                vigencias = vigencias.filter(fecha_vencimiento__lt=hoy)
            elif estado == 'proximo':
                vigencias = vigencias.filter(
                    fecha_vencimiento__range=[hoy, hoy + timedelta(days=7)]
                )
            elif estado == 'vigente':
                vigencias = vigencias.filter(fecha_vencimiento__gt=hoy + timedelta(days=7))
        
        if vehicle_id:
            vigencias = vigencias.filter(vehicle_id=vehicle_id)
    
    # Ordenar por fecha de vencimiento
    vigencias = vigencias.order_by('fecha_vencimiento')
    
    # Calcular días restantes
    hoy = timezone.localdate()
    for v in vigencias:
        v.dias_restantes = (v.fecha_vencimiento - hoy).days
    
    # Estadísticas
    total_vigencias = vigencias.count()
    vencimientos_proximos = sum(1 for v in vigencias if 0 < v.dias_restantes <= 7)
    vencimientos_hoy = sum(1 for v in vigencias if v.dias_restantes <= 0)
    
    # Plan del usuario
    profile = getattr(request.user, "profile", None)
    plan = profile.plan if profile else PlanChoices.FREE
    is_free = plan == PlanChoices.FREE
    
    # Límite de vigencias para free
    limite_free = 3
    porcentaje_uso = min(100, int((total_vigencias / limite_free) * 100)) if is_free else 100

    context = {
        "vehicles": vehicles,
        "vigencias": vigencias,
        "plan": plan,
        "is_free": is_free,
        "total_vigencias": total_vigencias,
        "vencimientos_proximos": vencimientos_proximos,
        "vencimientos_hoy": vencimientos_hoy,
        "porcentaje_uso": porcentaje_uso,
        "limite_free": limite_free,
        "today": hoy,
        "filter_form": filter_form,
        "official_services": official_services
    }
    return render(request, "core/dashboard.html", context)

@login_required
def vehicle_create(request):
    if request.method == "POST":
        alias = (request.POST.get("alias") or "").strip()
        plate = (request.POST.get("plate") or "").strip().upper()

        if not alias or len(alias) < 2:
            messages.error(request, "El nombre debe tener al menos 2 caracteres.")
            return render(request, "core/vehicle_form.html")
    
        if plate:
            try:
                validar_placa_colombiana(plate)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, "core/vehicle_form.html")
        
        if Vehicle.objects.filter(owner=request.user, alias=alias).exists():
            messages.warning(request, f"Ya tienes un vehículo llamado '{alias}'.")
        
        Vehicle.objects.create(owner=request.user, alias=alias, plate=plate)
        messages.success(request, f"Vehículo '{alias}' creado correctamente.")
        return redirect("dashboard")

    return render(request, "core/vehicle_form.html")


@login_required
def vigencia_create(request):
    profile = getattr(request.user, "profile", None)
    is_free = (not profile) or (profile.plan == PlanChoices.FREE)
    total_vigencias = Vigencia.objects.filter(vehicle__owner=request.user, activo=True).count()
    if is_free and total_vigencias >= 3:
        return render(request, "core/upgrade.html", {"total_vigencias": total_vigencias})

    vehicles = Vehicle.objects.filter(owner=request.user)
    if not vehicles.exists():
        messages.info(request, "Primero crea un vehículo para poder registrar una vigencia.")
        return redirect("vehicle_create")

    if request.method == "POST":
        vehicle_id = request.POST.get("vehicle_id")
        tipo = request.POST.get("tipo")
        fecha_str = request.POST.get("fecha_vencimiento")

        if not vehicle_id or not tipo or not fecha_str:
            messages.error(request, "Completa todos los campos.")
            return render(request, "core/vigencia_form.html", {"vehicles": vehicles})

        # Validación de fecha
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hoy = timezone.localdate()
            
            if fecha <= hoy:
                messages.error(request, "La fecha de vencimiento debe ser futura.")
                return render(request, "core/vigencia_form.html", {"vehicles": vehicles})
                
            # Validación: no más de 2 años en el futuro
            if fecha > hoy + timedelta(days=730):  # 2 años
                messages.error(request, "La fecha no puede ser mayor a 2 años en el futuro.")
                return render(request, "core/vigencia_form.html", {"vehicles": vehicles})
                
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return render(request, "core/vigencia_form.html", {"vehicles": vehicles})

        vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

        Vigencia.objects.create(
            vehicle=vehicle,
            tipo=tipo,
            fecha_vencimiento=fecha,
            activo=True,
            r30=True,
            r15=True,
            r7=True,
            r1=True,
        )
        messages.success(request, "Vigencia creada. Te avisaremos a tiempo por email (gratis).")
        return redirect("dashboard")

    return render(request, "core/vigencia_form.html", {"vehicles": vehicles})


@login_required
def vigencia_mark_renewed(request, pk: int):
    vig = get_object_or_404(Vigencia, pk=pk, vehicle__owner=request.user)

    # marcamos como inactiva (histórico)
    vig.activo = False
    vig.save(update_fields=["activo"])
    messages.success(request, "Listo: marcada como renovada.")
    return redirect("dashboard")





def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()

        if not username or not email or not password:
            messages.error(request, "Completa todos los campos.")
            return render(request, "core/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe. Intenta otro.")
            return render(request, "core/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ese correo ya está registrado.")
            return render(request, "core/register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Cuenta creada. Bienvenido a Mis Vigencias.")
        return redirect("dashboard")

    return render(request, "core/register.html")


@login_required
def pro_request(request):
    if request.method == "POST":
        note = (request.POST.get("note") or "").strip()

        subject = "[Mis Vigencias] Solicitud de PRO"
        body = (
            f"Usuario: {request.user.username}\n"
            f"Email: {request.user.email}\n"
            f"Nota: {note}\n"
        )

        # Te llega a ti (configuras este correo en settings/.env)
        admin_email = getattr(settings, "ADMIN_NOTIFY_EMAIL", "")
        if admin_email:
            send_mail(subject, body, None, [admin_email], fail_silently=True)

        messages.success(request, "Solicitud enviada. Te contactaremos para activar PRO.")
        return redirect("dashboard")

    return render(request, "core/pro_request.html")



@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    
    if request.method == "POST":
        alias = (request.POST.get("alias") or "").strip()
        plate = (request.POST.get("plate") or "").strip().upper()
        
        if not alias or len(alias) < 2:
            messages.error(request, "El nombre debe tener al menos 2 caracteres.")
            return render(request, "core/vehicle_form.html", {"vehicle": vehicle})
        
        # Validar placa si se proporciona
        if plate:
            try:
                validar_placa_colombiana(plate)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, "core/vehicle_form.html", {"vehicle": vehicle})
        
        vehicle.alias = alias
        vehicle.plate = plate
        vehicle.save()
        
        messages.success(request, f"Vehículo '{alias}' actualizado correctamente.")
        return redirect("dashboard")
    
    return render(request, "core/vehicle_form.html", {"vehicle": vehicle})

@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    
    if request.method == "POST":
        alias = vehicle.alias
        vehicle.delete()
        messages.success(request, f"Vehículo '{alias}' eliminado correctamente.")
        return redirect("dashboard")
    
    # Contar vigencias activas
    active_vigencias = Vigencia.objects.filter(vehicle=vehicle, activo=True).count()
    
    context = {
        "vehicle": vehicle,
        "active_vigencias": active_vigencias,
    }
    return render(request, "core/vehicle_confirm_delete.html", context)

@login_required
def vigencia_edit(request, pk):
    vigencia = get_object_or_404(Vigencia, pk=pk, vehicle__owner=request.user)
    vehicles = Vehicle.objects.filter(owner=request.user)
    
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        fecha_str = request.POST.get("fecha_vencimiento")
        
        if not tipo or not fecha_str:
            messages.error(request, "Completa todos los campos.")
            return render(request, "core/vigencia_form.html", {
                "vigencia": vigencia,
                "vehicles": vehicles
            })
        
        # Validación de fecha
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hoy = timezone.localdate()
            
            if fecha <= hoy:
                messages.error(request, "La fecha de vencimiento debe ser futura.")
                return render(request, "core/vigencia_form.html", {
                    "vigencia": vigencia,
                    "vehicles": vehicles
                })
                
            if fecha > hoy + timedelta(days=730):
                messages.error(request, "La fecha no puede ser mayor a 2 años en el futuro.")
                return render(request, "core/vigencia_form.html", {
                    "vigencia": vigencia,
                    "vehicles": vehicles
                })
                
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return render(request, "core/vigencia_form.html", {
                "vigencia": vigencia,
                "vehicles": vehicles
            })
        
        vigencia.tipo = tipo
        vigencia.fecha_vencimiento = fecha
        vigencia.save()
        
        messages.success(request, "Vigencia actualizada correctamente.")
        return redirect("dashboard")
    
    return render(request, "core/vigencia_form.html", {
        "vigencia": vigencia,
        "vehicles": vehicles
    })

@login_required
def vigencia_delete(request, pk):
    vigencia = get_object_or_404(Vigencia, pk=pk, vehicle__owner=request.user)
    
    if request.method == "POST":
        vigencia.delete()
        messages.success(request, "Vigencia eliminada correctamente.")
        return redirect("dashboard")
    
    return render(request, "core/vigencia_confirm_delete.html", {"vigencia": vigencia})


@login_required
def profile_settings(request):
    profile = getattr(request.user, 'profile', None)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # Actualizar profile
            if profile:
                profile.phone = form.cleaned_data.get('phone', '')
                profile.whatsapp_enabled = form.cleaned_data.get('whatsapp_enabled', False)
                profile.email_notifications = form.cleaned_data.get('email_notifications', True)
                
                # Convertir días seleccionados a lista de enteros
                notification_days = form.cleaned_data.get('notification_days', [])
                profile.notification_days = [int(day) for day in notification_days]
                
                profile.save()
                messages.success(request, 'Configuración actualizada correctamente.')
            else:
                messages.error(request, 'No se encontró el perfil.')
            
            return redirect('profile_settings')
    else:
        # Cargar datos actuales
        initial_data = {}
        if profile:
            initial_data = {
                'phone': profile.phone,
                'whatsapp_enabled': profile.whatsapp_enabled,
                'email_notifications': profile.email_notifications,
                'notification_days': [str(day) for day in profile.notification_days],
            }
        
        form = ProfileForm(initial=initial_data)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'core/profile_settings.html', context)