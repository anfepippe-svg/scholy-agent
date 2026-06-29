"""Plugin de seguridad (defense-in-depth, capa 2).

Un plugin del ADK intercepta el ciclo de vida de los agentes mediante callbacks.
Aquí usamos ``before_model_callback`` para inspeccionar lo que se va a enviar al
modelo y registrar posibles intentos de prompt injection que se hayan colado.

Es una SEGUNDA barrera: la primera (guardrails.py) ya filtró la entrada en la
API. Defensa en profundidad = varias capas, ninguna depende de las demás.
"""

from __future__ import annotations

import logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

from scholy.security.guardrails import detect_injection

logger = logging.getLogger("scholy.security")


class SecurityGuardrailPlugin(BasePlugin):
    """Inspecciona cada petición al modelo en busca de patrones de inyección."""

    def __init__(self) -> None:
        super().__init__(name="security_guardrail")
        self.flagged_requests = 0

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Escanea el contenido de la petición y registra señales sospechosas.

        No bloquea el flujo (evitamos falsos positivos que rompan la experiencia),
        pero deja una traza auditable. Para producción, aquí se podría devolver
        una LlmResponse para cortar la llamada o integrar Model Armor (GCP).
        """
        suspicious: list[str] = []
        for content in llm_request.contents or []:
            for part in getattr(content, "parts", None) or []:
                text = getattr(part, "text", None)
                if text:
                    suspicious.extend(detect_injection(text))

        if suspicious:
            self.flagged_requests += 1
            # Registramos el HECHO, no el contenido, para no filtrar PII a los logs.
            logger.warning(
                "[Seguridad] Petición marcada: %d patrón(es) de inyección detectado(s).",
                len(suspicious),
            )
