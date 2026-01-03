from django import forms
from .models import VigenciaType

class VigenciaFilterForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(VigenciaType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Todos los estados'),
            ('vencido', 'Vencido'),
            ('proximo', 'Próximo a vencer (≤7 días)'),
            ('vigente', 'Vigente (>7 días)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    vehicle = forms.ChoiceField(
        choices=[('', 'Todos los vehículos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user_vehicles = kwargs.pop('user_vehicles', None)
        super().__init__(*args, **kwargs)
        
        if user_vehicles:
            vehicle_choices = [('', 'Todos los vehículos')]
            vehicle_choices.extend([(v.id, v.alias) for v in user_vehicles])
            self.fields['vehicle'].choices = vehicle_choices
            
            


class ProfileForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567'
        }),
        label="Teléfono (WhatsApp)"
    )
    
    whatsapp_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Recibir notificaciones por WhatsApp (solo PRO)"
    )
    
    email_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Recibir notificaciones por email"
    )
    
    notification_days = forms.MultipleChoiceField(
        choices=[
            (30, '30 días antes'),
            (15, '15 días antes'),
            (7, '7 días antes'),
            (1, '1 día antes'),
            (0, 'El día del vencimiento'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Recordarme con"
    )