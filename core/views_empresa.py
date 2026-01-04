from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Empresa, UsuarioEmpresa, Vehicle, Vigencia
from .forms import EmpresaForm, InvitacionEmpresaForm
from django.utils import timezone
from datetime import timedelta

def es_admin_empresa(user):
    """Verifica si es admin de alguna empresa"""
    return UsuarioEmpresa.objects.filter(
        user=user,
        rol='ADMIN',
        activo=True
    ).exists()

@login_required
def empresa_dashboard(request):
    """Dashboard para empresas"""
    usuario_empresa = UsuarioEmpresa.objects.filter(
        user=request.user,
        activo=True
    ).first()
    
    if not usuario_empresa:
        return redirect('dashboard')
    
    empresa = usuario_empresa.empresa
    
    # Estadísticas
    total_vehiculos = empresa.vehiculos.count()
    total_vigencias = Vigencia.objects.filter(
        vehicle__empresa=empresa,
        activo=True
    ).count()
    
    vigencias_proximas = Vigencia.objects.filter(
        vehicle__empresa=empresa,
        activo=True,
        fecha_vencimiento__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    
    usuarios_activos = empresa.usuarios.filter(activo=True).count()
    
    context = {
        'empresa': empresa,
        'usuario_empresa': usuario_empresa,
        'stats': {
            'vehiculos': total_vehiculos,
            'vigencias': total_vigencias,
            'proximas': vigencias_proximas,
            'usuarios': usuarios_activos,
        }
    }
    
    return render(request, 'core/empresa_dashboard.html', context)

@login_required
@user_passes_test(es_admin_empresa)
def empresa_vehiculos(request):
    """Gestión de vehículos de empresa"""
    usuario_empresa = get_object_or_404(
        UsuarioEmpresa,
        user=request.user,
        activo=True,
        rol__in=['ADMIN', 'GERENTE']
    )
    
    vehiculos = Vehicle.objects.filter(
        empresa=usuario_empresa.empresa
    ).select_related('empresa').order_by('alias')
    
    return render(request, 'core/empresa_vehiculos.html', {
        'vehiculos': vehiculos,
        'empresa': usuario_empresa.empresa
    })

@login_required
@user_passes_test(es_admin_empresa)
def invitar_usuario(request):
    """Invitar usuario a empresa"""
    usuario_empresa = get_object_or_404(
        UsuarioEmpresa,
        user=request.user,
        activo=True,
        rol='ADMIN'
    )
    
    if request.method == 'POST':
        form = InvitacionEmpresaForm(request.POST)
        if form.is_valid():
            # Crear invitación (podrías crear modelo InvitacionEmpresa)
            email = form.cleaned_data['email']
            rol = form.cleaned_data['rol']
            
            # Enviar email de invitación
            # ...
            
            messages.success(request, f"Invitación enviada a {email}")
            return redirect('empresa_usuarios')
    else:
        form = InvitacionEmpresaForm()
    
    return render(request, 'core/invitar_usuario.html', {'form': form})