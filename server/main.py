"""Backend FastAPI de SCHOLY AGENT.

Conecta tres piezas:
  Frontend (formulario)  ->  /api/search  ->  ADK Runner (pipeline multiagente)

El Runner es el "motor" que ejecuta el root_agent dentro de una sesión, aplicando
los plugins de observabilidad y seguridad. Aquí traducimos el formulario del
usuario en un mensaje, lo sanitizamos, corremos el pipeline y devolvemos la
recomendación final como JSON para que el frontend la pinte.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel
from pathlib import Path

from scholy.config import settings
from scholy.observability import build_plugins, configure_logging
from scholy.schemas import Recommendation
from scholy.security.guardrails import is_safe_input, sanitize_user_input

# --- Inicialización ---------------------------------------------------
configure_logging(level=logging.INFO)
logger = logging.getLogger("scholy.server")

# Falla temprano y claro si falta la credencial.
settings.require_google_api_key()

# Importamos el agente raíz DESPUÉS de validar la config.
from scholy.agent import root_agent  # noqa: E402

app = FastAPI(title="SCHOLY AGENT", version="0.1.0")

# Un único Runner reutilizable: agente + plugins (observabilidad + seguridad).
runner = InMemoryRunner(agent=root_agent, app_name=settings.app_name, plugins=build_plugins())

_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
_USER_ID = "web_user"


class SearchRequest(BaseModel):
    """Cuerpo del formulario que llega del frontend (todo opcional salvo lo clave)."""

    academic_level: str
    field_of_study: str
    target_country: str | None = None
    nationality: str | None = None
    certified_languages: str | None = None  # texto libre separado por comas
    has_extra_income: bool = False
    needs_full_funding: bool = True
    gpa: float | None = None
    study_mode: str | None = None
    notes: str | None = None


def _build_user_message(req: SearchRequest) -> str:
    """Convierte el formulario en un mensaje en lenguaje natural para el pipeline.

    Sanitizamos los campos de texto libre (notes, idiomas) como defensa adicional.
    """
    safe_notes = sanitize_user_input(req.notes) if req.notes else ""
    safe_langs = sanitize_user_input(req.certified_languages) if req.certified_languages else ""
    # Inyectamos la fecha real de hoy: el modelo no la conoce por sí mismo, y la
    # necesita para descartar becas cuyo plazo de postulación ya venció.
    lines = [
        f"Fecha de hoy (referencia para deadlines): {date.today().isoformat()}",
        "Perfil del estudiante para búsqueda de becas:",
        f"- Nivel académico: {req.academic_level}",
        f"- Área de estudio: {req.field_of_study}",
        f"- País objetivo: {req.target_country or 'sin preferencia'}",
        f"- Nacionalidad: {req.nationality or 'no especificada'}",
        f"- Idiomas certificados: {safe_langs or 'no especificados'}",
        f"- ¿Tiene ingreso extra para manutención?: {'sí' if req.has_extra_income else 'no'}",
        f"- ¿Necesita financiación completa?: {'sí' if req.needs_full_funding else 'no'}",
        f"- GPA: {req.gpa if req.gpa is not None else 'no especificado'}",
        f"- Modalidad: {req.study_mode or 'indiferente'}",
        f"- Notas: {safe_notes or 'ninguna'}",
    ]
    return "\n".join(lines)


async def _run_pipeline(message: str) -> str:
    """Ejecuta el pipeline multiagente y devuelve el texto de la respuesta final."""
    session_id = str(uuid.uuid4())
    await runner.session_service.create_session(
        app_name=settings.app_name, user_id=_USER_ID, session_id=session_id
    )
    content = types.Content(role="user", parts=[types.Part(text=message)])

    final_text = ""
    async for event in runner.run_async(
        user_id=_USER_ID, session_id=session_id, new_message=content
    ):
        # Nos quedamos con el último texto producido (lo emite el AdvisorAgent).
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_text = part.text
    return final_text


@app.post("/api/search", response_model=Recommendation)
async def search(req: SearchRequest) -> Recommendation:
    """Endpoint principal: recibe el perfil y devuelve becas recomendadas."""
    message = _build_user_message(req)

    # Guardrail capa 1: validar la entrada antes de gastar tokens.
    safe, reason = is_safe_input(message)
    if not safe:
        logger.warning("[Seguridad] Entrada rechazada: %s", reason)
        raise HTTPException(status_code=400, detail="Entrada no válida.")

    try:
        raw = await _run_pipeline(message)
    except Exception as exc:  # noqa: BLE001
        # Caso frecuente en capa gratuita: cuota agotada (429 RESOURCE_EXHAUSTED).
        # Lo detectamos por el mensaje y devolvemos un 429 con texto entendible,
        # en vez de un 500 genérico. Esto NO es alucinación: la petición falla.
        msg = str(exc)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            logger.warning("[Cuota] Límite gratuito de Gemini alcanzado.")
            raise HTTPException(
                status_code=429,
                detail=(
                    "Se alcanzó el límite gratuito de Gemini por hoy. "
                    "Espera unos minutos o inténtalo de nuevo mañana."
                ),
            ) from exc
        logger.exception("Error ejecutando el pipeline.")
        raise HTTPException(status_code=500, detail="Error interno del agente.") from exc

    # El AdvisorAgent devuelve JSON validable contra Recommendation.
    try:
        return Recommendation.model_validate_json(raw)
    except Exception:  # noqa: BLE001
        # Fallback: si no vino JSON limpio, devolvemos el texto como resumen.
        logger.warning("La salida final no era JSON válido; devolviendo texto plano.")
        return Recommendation(summary=raw or "No se obtuvieron resultados.", scholarships=[])


@app.get("/")
async def index() -> FileResponse:
    """Sirve la página principal del frontend."""
    return FileResponse(_FRONTEND_DIR / "index.html")


# Sirve los archivos estáticos del frontend (app.js, etc.).
app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")
