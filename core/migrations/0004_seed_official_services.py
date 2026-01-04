from django.db import migrations


def seed_services(apps, schema_editor):
    OfficialService = apps.get_model("core", "OfficialService")

    data = [
        dict(
            key="simit",
            title="Comparendos / SIMIT",
            description="Consulta y pago de multas y sanciones de tránsito.",
            url="https://fcm.org.co/simit",
            icon="bi-receipt-cutoff",
            note="Federación Colombiana de Municipios (SIMIT oficial).",
            is_active=True,
            sort_order=10,
        ),
        dict(
            key="runt_placa",
            title="RUNT - Consulta por placa",
            description="Consulta de información del vehículo por placa (RUNT).",
            url="https://www.runt.gov.co/actores/ciudadano/consulta-de-vehiculos-por-placa",
            icon="bi-card-checklist",
            note="Portal oficial del RUNT.",
            is_active=True,
            sort_order=20,
        ),
        dict(
            key="runt_historico",
            title="RUNT - Histórico vehicular",
            description="Consulta histórico vehicular desde el portal ciudadano.",
            url="https://www.runt.gov.co/actores/ciudadano/consulta-historico-vehicular",
            icon="bi-clock-history",
            note="",
            is_active=True,
            sort_order=30,
        ),
        dict(
            key="rnmc",
            title="RNMC - Medidas correctivas",
            description="Consulta de medidas correctivas (Policía Nacional).",
            url="https://srvcnpc.policia.gov.co/PSC/frm_cnp_consulta.aspx",
            icon="bi-shield-exclamation",
            note="",
            is_active=True,
            sort_order=40,
        ),
        dict(
            key="siniestros_fasecolda",
            title="Historial de siniestros (Fasecolda)",
            description="Consulta historial de accidentes/siniestros de vehículos asegurados.",
            url="https://www.fasecolda.com/ramos/automoviles/historial-de-accidentes-de-vehiculos-asegurados/",
            icon="bi-car-front",
            note="Requiere validación/captcha según el portal.",
            is_active=True,
            sort_order=50,
        ),
    ]

    for row in data:
        OfficialService.objects.update_or_create(key=row["key"], defaults=row)


def unseed_services(apps, schema_editor):
    OfficialService = apps.get_model("core", "OfficialService")
    OfficialService.objects.filter(
        key__in=["simit", "runt_placa", "runt_historico", "rnmc", "siniestros_fasecolda"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_officialservice"),
    ]

    operations = [
        migrations.RunPython(seed_services, reverse_code=unseed_services),
    ]
