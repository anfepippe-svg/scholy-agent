"""AdvisorAgent: produce la recomendación final estructurada.

Es el último agente del pipeline. Toma las becas elegibles y arma la salida
final: un resumen accionable + la lista de becas con su análisis financiero,
en un JSON validado contra el modelo Recommendation (listo para el frontend).

Conceptos ADK demostrados:
- output_schema: salida estructurada y validada (clave para una UI confiable).
  Recuerda: un agente con output_schema NO puede usar tools; por eso el cálculo
  determinista ya se hizo en el EligibilityAgent.
- El análisis financiero responde a una necesidad real del usuario: no basta con
  que la beca exista, debe poder vivir mientras estudia.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent

from scholy.llm import build_model
from scholy.schemas import Recommendation

_INSTRUCTION = """Eres el agente ASESOR de SCHOLY, un coach financiero estudiantil.

Perfil del estudiante:
{student_profile}

Becas elegibles (ya filtradas y puntuadas):
{eligible_scholarships}

Tu tarea: construir la recomendación final para el estudiante.
- Para cada beca, completa el campo financial_fit explicando el encaje financiero:
  ¿cubre solo matrícula o también manutención? Si el estudiante necesita
  financiación completa (needs_full_funding) y la beca solo cubre matrícula,
  adviértelo y menciona qué tendría que costear (vivienda, comida, transporte).
- Conserva EXACTAMENTE el match_score que ya trae cada beca del paso anterior.
  Si una beca no tiene match_score calculado, deja el campo como null (NO pongas
  0; un 0 confundiría al estudiante). Nunca inventes un puntaje.
- Conserva la URL tal cual viene; si está vacía o no es un enlace http(s) válido
  y limpio, déjala vacía (null). No construyas ni completes URLs.
- Ordena las becas de mayor a menor match_score (las que no tengan puntaje van al final).
- Escribe un 'summary' breve, claro y accionable (2-4 frases).

Devuelve EXCLUSIVAMENTE el objeto final en el formato estructurado solicitado.
No inventes becas que no estén en la lista de elegibles.
"""

advisor_agent = LlmAgent(
    name="AdvisorAgent",
    model=build_model(),
    description="Genera la recomendación final con tabla comparativa y análisis financiero.",
    instruction=_INSTRUCTION,
    output_schema=Recommendation,
    output_key="final_recommendation",
)
