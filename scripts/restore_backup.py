#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import boto3
from django.conf import settings

def restore_from_s3(backup_name):
    """Restaure desde S3"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    backup_path = Path(f"backups/{backup_name}")
    backup_path.parent.mkdir(exist_ok=True)
    
    try:
        s3.download_file(
            settings.AWS_BACKUP_BUCKET,
            f"database/{backup_name}",
            str(backup_path)
        )
        print(f"✓ Backup descargado: {backup_name}")
        return backup_path
    except Exception as e:
        print(f"✗ Error descargando: {e}")
        return None

def restore_database(backup_path):
    """Restaurar base de datos"""
    cmd = [
        'psql',
        '-h', settings.DATABASES['default']['HOST'],
        '-U', settings.DATABASES['default']['USER'],
        '-d', settings.DATABASES['default']['NAME'],
        '-f', str(backup_path)
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']
    
    try:
        print("⚠️ Restaurando base de datos...")
        subprocess.run(cmd, env=env, check=True)
        print("✅ Base de datos restaurada")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error restaurando: {e}")
        return False

def list_backups():
    """Lista backups disponibles"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    response = s3.list_objects_v2(
        Bucket=settings.AWS_BACKUP_BUCKET,
        Prefix="database/backup_"
    )
    
    backups = []
    for obj in response.get('Contents', []):
        backups.append(obj['Key'].replace('database/', ''))
    
    return backups

if __name__ == "__main__":
    # Uso: python restore_backup.py [backup_name]
    if len(sys.argv) > 1:
        backup_name = sys.argv[1]
    else:
        # Listar backups disponibles
        print("Backups disponibles:")
        for backup in list_backups():
            print(f"  - {backup}")
        sys.exit(0)
    
    print(f"🔄 Restaurando {backup_name}...")
    
    # 1. Descargar de S3
    backup_path = restore_from_s3(backup_name)
    if not backup_path:
        sys.exit(1)
    
    # 2. Restaurar
    restore_database(backup_path)