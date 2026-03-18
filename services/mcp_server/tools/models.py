"""
Modelos de datos (Pydantic)

Ventajas:
- Tipado fuerte
- Validación automática
- Compatible con MCP Inspector
"""

from pydantic import BaseModel
from typing import List, Optional


class SeverityResponse(BaseModel):
    severity: str
    confidence: float
    reasoning: str
    recommended_actions: List[str]
    as_of: str


class NotificationResponse(BaseModel):
    notification_required: bool
    authorities: List[str]
    deadline_hours: Optional[int]
    legal_basis: str
    contact_info: dict
    as_of: str


class CSIRTResponse(BaseModel):
    csirt: str
    is_available: bool
    specialization: Optional[str] = None
    contact: Optional[str] = None
    error: Optional[str] = None
    as_of: str