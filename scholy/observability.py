"""Observabilidad (Agent Ops): logging y métricas de ejecución.

Los agentes son estocásticos: para confiar en ellos hay que poder VER qué hacen.
Aquí proveemos:
1. ``configure_logging``: logging a archivo + consola.
2. ``CountInvocationPlugin``: cuenta agentes, peticiones al modelo y herramientas.
3. ``build_plugins``: junta los plugins de observabilidad y seguridad para el Runner.

El ADK también trae ``LoggingPlugin`` (logs detallados) y, en desarrollo, la
pestaña Events de ``adk web`` muestra los traces (spans call_llm, execute_tool,
tokens y tiempos). En producción usamos plugins porque no hay UI web.
"""

from __future__ import annotations

import logging

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.plugins.logging_plugin import LoggingPlugin

from scholy.security.plugins import SecurityGuardrailPlugin

logger = logging.getLogger("scholy")


def configure_logging(level: int = logging.INFO, log_file: str = "scholy.log") -> None:
    """Configura logging hacia archivo y consola (idempotente)."""
    root = logging.getLogger()
    if root.handlers:  # Evita duplicar handlers si se llama más de una vez.
        return
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(file_handler)


class CountInvocationPlugin(BasePlugin):
    """Plugin de métricas: cuenta ejecuciones de agentes y llamadas al modelo.

    Útil para detectar costos inesperados (p. ej. demasiadas llamadas al LLM) y
    para el video/demo: demuestra observabilidad programática sin la UI web.
    """

    def __init__(self) -> None:
        super().__init__(name="count_invocation")
        self.agent_count = 0
        self.llm_request_count = 0

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        self.agent_count += 1
        logger.info("[Métricas] Agente '%s' ejecutado (total: %d).", agent.name, self.agent_count)

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        self.llm_request_count += 1
        logger.info("[Métricas] Llamadas al modelo: %d.", self.llm_request_count)


def build_plugins() -> list[BasePlugin]:
    """Lista de plugins para inyectar en el Runner (orden = orden de ejecución).

    Combina observabilidad (LoggingPlugin + conteo) y seguridad (guardrail).
    """
    return [
        LoggingPlugin(),
        CountInvocationPlugin(),
        SecurityGuardrailPlugin(),
    ]
