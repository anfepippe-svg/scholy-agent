"""Configuración central de SCHOLY AGENT.

Toda la configuración se lee de variables de entorno (cargadas desde .env).
Esto cumple el principio de "cero API keys en el código": ningún secreto
queda escrito en los archivos fuente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carga el archivo .env (si existe) a las variables de entorno del proceso.
# En producción las variables vendrían del entorno del contenedor, no de .env.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Ajustes inmutables del sistema, derivados del entorno."""

    # Modelo de Gemini usado por todos los agentes.
    model: str = os.getenv("SCHOLY_MODEL", "gemini-2.5-flash-lite")

    # Nombre lógico de la app (lo usa el Runner/SessionService del ADK).
    app_name: str = "scholy_agent"

    # Clave opcional para una búsqueda externa vía MCP (V2). Vacía en el MVP.
    external_search_api_key: str | None = os.getenv("SCHOLY_EXTERNAL_SEARCH_API_KEY") or None

    def require_google_api_key(self) -> str:
        """Devuelve la GOOGLE_API_KEY o falla con un mensaje claro.

        Validamos explícitamente para que, si falta la credencial, el error
        sea entendible en vez de un fallo opaco dentro del SDK.
        """
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError(
                "Falta GOOGLE_API_KEY. Copia .env.example a .env y agrega tu "
                "API key gratuita de Google AI Studio (https://aistudio.google.com/apikey)."
            )
        return key


# Instancia única reutilizable en todo el proyecto.
settings = Settings()
