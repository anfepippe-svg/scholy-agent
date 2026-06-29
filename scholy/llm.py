"""Fábrica del modelo Gemini compartida por todos los agentes.

Centralizar la creación del modelo evita repetir configuración y garantiza
que todos los agentes usen el mismo modelo y la misma política de reintentos.
"""

from __future__ import annotations

from google.adk.models.google_llm import Gemini
from google.genai import types

from scholy.config import settings

# Reintentos ante errores transitorios (límites de cuota, fallos temporales).
# Importante en la capa GRATUITA de Gemini, donde el 429 es frecuente.
_RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def build_model() -> Gemini:
    """Crea una instancia de Gemini con el modelo y reintentos configurados."""
    return Gemini(model=settings.model, retry_options=_RETRY_CONFIG)
