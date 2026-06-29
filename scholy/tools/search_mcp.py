"""Conector OPCIONAL a un servidor MCP de búsqueda externa (camino V2).

Concepto demostrado: MCP (Model Context Protocol).
MCP es un estándar abierto para conectar agentes con herramientas/datos externos
que viven en un "servidor MCP" separado. El ADK los integra con ``McpToolset``.

En el MVP NO se usa: la búsqueda va por la herramienta integrada google_search,
que es gratis y no requiere claves. Este módulo deja preparado el camino para
enchufar, en una V2, un servidor MCP de búsqueda (p. ej. Tavily/Serper) sin
tocar el resto del sistema. Se activa solo si hay una API key configurada.

Cómo se usaría (ejemplo conceptual, comentado para no requerir dependencias ni
claves en el MVP):

    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    external_search_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "tavily-mcp"],
                # La clave llega por entorno: NUNCA se escribe en el código.
                env={"TAVILY_API_KEY": settings.external_search_api_key},
            ),
            timeout=30,
        )
    )
    # Luego: search_agent.tools.append(external_search_toolset)
"""

from __future__ import annotations

from scholy.config import settings


def external_search_enabled() -> bool:
    """Indica si el camino de búsqueda externa por MCP está configurado.

    En el MVP devuelve False (no hay API key), así el sistema usa google_search.
    """
    return settings.external_search_api_key is not None


def build_external_search_toolset():
    """Construiría el McpToolset de búsqueda externa (solo V2).

    Se mantiene como stub para no añadir dependencias ni requerir claves en el
    MVP. Si se activa en V2, aquí se devolvería un ``McpToolset`` configurado.
    """
    raise NotImplementedError(
        "Búsqueda externa por MCP no habilitada en el MVP. "
        "Configura SCHOLY_EXTERNAL_SEARCH_API_KEY e implementa el McpToolset para V2."
    )
