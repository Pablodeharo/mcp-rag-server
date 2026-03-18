"""
Notification Tool

Módulo que evalua si un incidente de ciberseguridad 
requiere notificación obligatoria a autoridades.

La lógica se basa en:
- ENS (Esquema Nacional de Seguridad)
- RGPD
- Directiva NIS2 (Normativa de la Union Europea)


"""
from datetime import datetime, timezone
from .models import NotificationResponse

# Palabras clave regulatorias
NOTIFICATION_TRIGGERS = {
    "ens_high": ["organismos públicos", "infraestructura crítica"],
    "rgpd": ["datos personales", "breach", "filtración"],
    "nis2": ["servicios esenciales", "telecomunicaciones", "energía"],
}

def notification_required(
    incident_type: str,
    affected_entity: str,
    data_breach: bool = False
) -> NotificationResponse:
    """
    Determina si un incidente requiere notificación legal.
    """

    authorities = []
    legal_basis = []

    entity_lower = affected_entity.lower()

    # ENS
    if any(kw in entity_lower for kw in NOTIFICATION_TRIGGERS["ens_high"]):
        authorities.append("CCN-CERT")
        legal_basis.append("ENS")

    # RGPD
    if data_breach or any(
        kw in incident_type.lower()
        for kw in ["breach", "filtración"]
    ):
        authorities.append("AEPD")
        legal_basis.append("RGPD")

    # NIS2
    if any(kw in entity_lower for kw in NOTIFICATION_TRIGGERS["nis2"]):
        authorities.append("INCIBE")
        legal_basis.append("NIS2")

    return NotificationResponse(
        notification_required=len(authorities) > 0,
        authorities=authorities if authorities else ["No aplica"],
        deadline_hours=72 if authorities else None,
        legal_basis=" + ".join(legal_basis) if legal_basis else "No aplica",
        contact_info=_get_contacts(authorities),
        as_of=datetime.now(timezone.utc).isoformat(),
    )


def _get_contacts(authorities: list[str]) -> dict:
    """
    Devuelve URLs oficiales de contacto.
    (SIN CAMBIOS)
    """

    contacts = {
        "CCN-CERT": "https://www.ccn-cert.cni.es",
        "AEPD": "https://www.aepd.es/reportar-brecha",
        "INCIBE": "https://www.incibe.es/protege-tu-empresa/notificacion-incidentes",
    }

    return {auth: contacts.get(auth, "N/A") for auth in authorities}