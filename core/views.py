from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .models import Vehicle, Vigencia, PlanChoices


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    vehicles = Vehicle.objects.filter(owner=request.user).prefetch_related("vigencias")
    vigencias = Vigencia.objects.filter(vehicle__owner=request.user, activo=True).select_related("vehicle")

    # límite FREE
    profile = getattr(request.user, "profile", None)
    plan = profile.plan if profile else PlanChoices.FREE
    is_free = plan == PlanChoices.FREE
    total_vigencias = Vigencia.objects.filter(vehicle__owner=request.user, activo=True).count()

    context = {
        "vehicles": vehicles,
        "vigencias": vigencias,
        "plan": plan,
        "is_free": is_free,
        "total_vigencias": total_vigencias,
        "today": timezone.localdate(),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def vehicle_create(request):
    if request.method == "POST":
        alias = (request.POST.get("alias") or "").strip()
        plate = (request.POST.get("plate") or "").strip().upper()

        if not alias:
            messages.error(request, "Por favor escribe un nombre para tu vehículo (ej: Mi moto, Duster).")
            return render(request, "core/vehicle_form.html")

        Vehicle.objects.create(owner=request.user, alias=alias, plate=plate)
        messages.success(request, "Vehículo creado correctamente.")
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
        fecha = request.POST.get("fecha_vencimiento")

        if not vehicle_id or not tipo or not fecha:
            messages.error(request, "Completa todos los campos.")
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