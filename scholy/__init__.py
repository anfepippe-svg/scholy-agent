"""SCHOLY AGENT: sistema multiagente (Google ADK) para encontrar becas.

El agente raíz se expone como ``root_agent`` para seguir la convención del
ADK (``adk web`` / ``adk run`` buscan ese símbolo).
"""

from scholy.agent import root_agent

__all__ = ["root_agent"]
