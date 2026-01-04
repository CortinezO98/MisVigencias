#!/usr/bin/env python3
import os
import sys
import datetime
import subprocess
from pathlib import Path
import boto3
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

def backup_database():
    """Backup de base de datos PostgreSQL"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    backup_path = BASE_DIR / "backups" / backup_file
    
    # Crear directorio si no existe
    backup_path.parent.mkdir(exist_ok=True)
    
    # Comando de backup (PostgreSQL)
    cmd = [
        'pg_dump',
        '-h', settings.DATABASES['default']['HOST'],
        '-U', settings.DATABASES['default']['USER'],
        '-d', settings.DATABASES['default']['NAME'],
        '-f', str(backup_path)
    ]
    
    # Setear password en entorno
    env = os.environ.copy()
    env['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"✓ Backup creado: {backup_file}")
        return backup_path
    except subprocess.CalledProcessError as e:
        print(f"✗ Error en backup: {e}")
        return None

def upload_to_s3(file_path):
    """Sube backup a S3"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket_name = settings.AWS_BACKUP_BUCKET
    s3_key = f"database/{file_path.name}"
    
    try:
        s3.upload_file(str(file_path), bucket_name, s3_key)
        print(f"✓ Backup subido a S3: {s3_key}")
        return True
    except Exception as e:
        print(f"✗ Error subiendo a S3: {e}")
        return False

def cleanup_old_backups(days_to_keep=7):
    """Elimina backups antiguos"""
    backup_dir = BASE_DIR / "backups"
    
    for file in backup_dir.glob("backup_*.sql"):
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(file.stat().st_mtime)
        if file_age.days > days_to_keep:
            file.unlink()
            print(f"✓ Eliminado backup antiguo: {file.name}")

def main():
    print("🔄 Iniciando backup automático...")
    
    # 1. Backup de base de datos
    backup_file = backup_database()
    if not backup_file:
        sys.exit(1)
    
    # 2. Subir a S3 (si está configurado)
    if all([
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY,
        settings.AWS_BACKUP_BUCKET
    ]):
        upload_to_s3(backup_file)
    
    # 3. Limpiar backups antiguos locales
    cleanup_old_backups()
    
    print("✅ Backup completado exitosamente")

if __name__ == "__main__":
    main()