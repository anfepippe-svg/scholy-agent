"""EligibilityAgent: filtra y puntúa las becas según el perfil.

Toma las becas crudas del SearchAgent y el perfil del ProfileAgent, descarta las
que el estudiante no puede aplicar y asigna un puntaje de compatibilidad usando
la herramienta determinista ``compute_compatibility_score``.

Conceptos ADK demostrados:
- Uso de FunctionTool dentro de un agente (función Python pasada directamente).
- Combinación de dos claves de estado en la instrucción: {student_profile} y
  {raw_scholarships}, ambas producidas por agentes anteriores del pipeline.
"""

from __future__ import annotations

from datetime import date

from google.adk.agents import LlmAgent

from scholy.llm import build_model
from scholy.tools.scholarship_tools import compute_compatibility_score

_INSTRUCTION = """Eres el agente de ELEGIBILIDAD de SCHOLY.

Perfil del estudiante:
{student_profile}

Becas encontradas (sin filtrar):
{raw_scholarships}

Tu tarea:
1. Por cada beca, evalúa si el estudiante es ELEGIBLE comparando:
   - nivel académico, área de estudio, país (si el estudiante indicó uno),
   - requisito de idioma vs idiomas certificados,
   - restricciones de nacionalidad y GPA mínimo.
2. Para cada beca candidata, llama a la herramienta `compute_compatibility_score`
   pasando los booleanos correspondientes. Usa su 'score' como match_score.
   - country_matches = true si el estudiante no indicó país.
   - gpa_ok = true si la beca no exige un GPA mínimo.
3. Descarta las becas claramente NO elegibles (p. ej. nacionalidad excluida o
   idioma que el estudiante no domina y no puede certificar).
4. DEADLINES (importante): la fecha de hoy es {today}. DESCARTA toda beca cuyo
   plazo de postulación ya haya pasado respecto a hoy. Conserva solo las que aún
   se pueden postular (deadline futuro) o las recurrentes con una próxima
   convocatoria. Si el deadline es desconocido o ambiguo, consérvala pero NO
   inventes una fecha.

Devuelve la lista de becas elegibles, cada una con su match_score y una breve
razón de elegibilidad. Ordénalas de mayor a menor match_score.
Si ninguna es elegible, dilo claramente.
"""

# Rellenamos solo {today} con la fecha real; {student_profile} y {raw_scholarships}
# quedan intactos para que el ADK los sustituya desde el estado de la sesión.
_INSTRUCTION = _INSTRUCTION.replace("{today}", date.today().isoformat())

eligibility_agent = LlmAgent(
    name="EligibilityAgent",
    model=build_model(),
    description="Filtra las becas por elegibilidad y las puntúa con una herramienta determinista.",
    instruction=_INSTRUCTION,
    # La función se pasa directamente: el ADK la envuelve como FunctionTool.
    tools=[compute_compatibility_score],
    output_key="eligible_scholarships",
)
