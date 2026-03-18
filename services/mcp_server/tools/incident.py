"""
Incident Severity Tool

Clasifica severidad en palabras clave.
Inspirado la clasificación de incidentes utilizados por organismos como INCIBE

Componente que se integra en pipelines RAG

"""

from datetime import datetime, timezone
from typing import Literal
from .models import SeverityResponse

# Criterios de severidad
SEVERITY_CRITERIA = {
    "critical": ["ransomware", "data breach", "ddos", "apt", "zero-day"],
    "high": ["malware", "phishing masivo", "compromiso de credenciales"],
    "medium": ["spam", "phishing aislado", "vulnerabilidad conocida"],
    "low": ["falso positivo", "configuración errónea"],
}

def incident_severity(description: str) -> SeverityResponse:
    """
    Clasifica severidad del incidente.

    Ahora devuelve un modelo Pydantic en vez de dict.
    """

    description_lower = description.lower()

    for severity, keywords in SEVERITY_CRITERIA.items():
        if any(kw in description_lower for kw in keywords):

            return SeverityResponse(
                severity=severity,
                confidence=0.85,
                reasoning=f"Detectadas palabras clave asociadas a nivel {severity}",
                recommended_actions=_get_actions(severity),
                as_of=datetime.now(timezone.utc).isoformat(),
            )

    # Caso por defecto (SIN CAMBIOS)
    return SeverityResponse(
        severity="medium",
        confidence=0.5,
        reasoning="No se detectaron indicadores claros, asignación por defecto",
        recommended_actions=[
            "Evaluar manualmente",
            "Recopilar más información"
        ],
        as_of=datetime.now(timezone.utc).isoformat(),
    )


def _get_actions(severity: str) -> list[str]:
    """
    Acciones recomendadas según severidad.
    (SIN CAMBIOS)
    """

    actions = {
        "critical": [
            "Activar CSIRT inmediatamente",
            "Contener sistema afectado",
            "Notificar a dirección"
        ],
        "high": [
            "Evaluar alcance",
            "Iniciar contención",
            "Documentar evidencias"
        ],
        "medium": [
            "Monitorizar",
            "Aplicar parches",
            "Revisar logs"
        ],
        "low": [
            "Documentar",
            "Revisar configuración"
        ],
    }

    return actions.get(severity, ["Evaluar manualmente"])