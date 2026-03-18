"""
CSIRT Availability Tool

Consulta disponibilidad de equipos CSIRT nacionales.
Permite al agante conocer si existe soporte 24/ y alguna especialidad.
"""

from datetime import datetime, timezone
from .models import CSIRTResponse

CSIRT_TEAMS = {
    "CCN-CERT": {
        "available_24_7": True, 
        "specialization": "Administraciones públicas"
    },
    "INCIBE-CERT": {
        "available_24_7": True, 
        "specialization": "Empresas privadas"
    },
    "CSIRT-CV": {
        "available_24_7": False, 
        "hours": "9:00-18:00",
        "specialization": "Regional"
    },
}

def csirt_availability(csirt_name: str) -> CSIRTResponse:
    """
    Consulta disponibilidad de CSIRT.
    """

    team = CSIRT_TEAMS.get(csirt_name)

    # Caso: no encontrado (SIN CAMBIOS)
    if not team:
        return CSIRTResponse(
            csirt=csirt_name,
            is_available=False,
            error="CSIRT no reconocido",
            as_of=datetime.now(timezone.utc).isoformat(),
        )

    # Caso: encontrado
    return CSIRTResponse(
        csirt=csirt_name,
        is_available=team["available_24_7"],
        specialization=team["specialization"],
        contact=f"https://www.{csirt_name.lower().replace('-', '')}.es/contacto",
        as_of=datetime.now(timezone.utc).isoformat(),
    )