import re
from django.core.exceptions import ValidationError

def validar_placa_colombiana(value):
    """
    Valida formatos de placas colombianas:
    - Formato antiguo: AAA123 o CCC123 (3 letras, 3 números)
    - Formato nuevo: ABC123D (3 letras, 3 números, 1 letra)
    """
    if not value:
        return  
    
    value = value.upper().strip()
    
    patron_antiguo = r'^[A-Z]{3}\d{3}$'  
    patron_nuevo = r'^[A-Z]{3}\d{3}[A-Z]$'  
    
    if not (re.match(patron_antiguo, value) or re.match(patron_nuevo, value)):
        raise ValidationError(
            'Formato de placa inválido. Use: AAA123 o ABC123D',
            params={'value': value},
        )