import os
from PIL import Image
from django.core.files.storage import default_storage
from django.conf import settings
import PyPDF2
from io import BytesIO

def validate_document_size(file):
    """Valida tamaño máximo (10MB)"""
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(f"El archivo es muy grande (máximo 10MB)")
    return True

def compress_image(image_path, quality=85):
    """Comprime imagen manteniendo calidad"""
    img = Image.open(image_path)
    
    # Convertir a RGB si es RGBA
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img, mask=img.getchannel('A'))
        img = background
    
    # Redimensionar si es muy grande
    max_width = 1920
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Guardar comprimido
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return output

def extract_pdf_info(pdf_file):
    """Extrae información básica de PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Intentar extraer texto de la primera página
        text = ""
        if num_pages > 0:
            page = pdf_reader.pages[0]
            text = page.extract_text()[:500]  # Primeros 500 caracteres
        
        return {
            'pages': num_pages,
            'preview_text': text,
            'encrypted': pdf_reader.is_encrypted
        }
    except:
        return {'pages': 0, 'preview_text': '', 'encrypted': False}

def generate_thumbnail(image_file, size=(300, 300)):
    """Genera thumbnail para vista previa"""
    img = Image.open(image_file)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=70)
    output.seek(0)
    
    return output

def is_safe_filename(filename):
    """Valida que el nombre de archivo sea seguro"""
    forbidden = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    return not any(char in filename for char in forbidden)