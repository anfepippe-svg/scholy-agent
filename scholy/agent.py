"""Agente raíz de SCHOLY: orquesta el pipeline multiagente.

Patrón usado: SequentialAgent (línea de ensamblaje). La salida de cada agente
alimenta al siguiente a través del estado de la sesión (output_key -> {clave}):

    ProfileAgent      -> student_profile
    SearchAgent       -> raw_scholarships
    EligibilityAgent  -> eligible_scholarships
    AdvisorAgent      -> final_recommendation  (salida final estructurada)

Elegimos Sequential porque el flujo es naturalmente lineal: primero entender al
estudiante, luego buscar, luego filtrar y finalmente aconsejar. Cada agente es
un "especialista" pequeño y mantenible (equipo de especialistas > súper-agente).

Este símbolo ``root_agent`` es el que descubren ``adk web`` y ``adk run``.
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent

from scholy.agents.advisor_agent import advisor_agent
from scholy.agents.eligibility_agent import eligibility_agent
from scholy.agents.profile_agent import profile_agent
from scholy.agents.search_agent import search_agent

root_agent = SequentialAgent(
    name="ScholyCoordinator",
    description=(
        "Coordinador de SCHOLY: convierte el perfil de un estudiante en una lista "
        "de becas recomendadas, filtradas por elegibilidad y con análisis financiero."
    ),
    sub_agents=[
        profile_agent,
        search_agent,
        eligibility_agent,
        advisor_agent,
    ],
)
