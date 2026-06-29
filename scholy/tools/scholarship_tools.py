"""Herramientas (FunctionTools) deterministas para evaluar becas.

¿Por qué herramientas y no dejar que el LLM "calcule"? Porque un puntaje debe
ser REPRODUCIBLE y AUDITABLE. La lógica de negocio crítica vive en código Python
determinista; el agente solo decide CUÁNDO llamarla. Esto es justo lo que el
curso llama "deterministic guardrails": reglas rígidas en el código.

Concepto ADK demostrado:
- FunctionTool: una función Python normal se expone como herramienta. El ADK
  lee la firma y el docstring para que el modelo sepa cómo y cuándo usarla.
  El docstring es parte del "prompt": debe ser claro y describir los argumentos.
"""

from __future__ import annotations


def compute_compatibility_score(
    level_matches: bool,
    field_matches: bool,
    country_matches: bool,
    language_ok: bool,
    gpa_ok: bool,
    covers_full_costs: bool,
) -> dict:
    """Calcula un puntaje de compatibilidad 0-100 entre una beca y un estudiante.

    Cada criterio aporta un peso fijo y determinista. Úsala una vez por beca
    candidata para obtener un puntaje comparable y explicable.

    Args:
        level_matches: La beca corresponde al nivel académico buscado.
        field_matches: El área de estudio coincide o es compatible.
        country_matches: La beca está en el país deseado (True si no hay preferencia).
        language_ok: El estudiante cumple el requisito de idioma de la beca.
        gpa_ok: El estudiante cumple el GPA mínimo (True si la beca no exige uno).
        covers_full_costs: La beca cubre lo que el estudiante necesita financiar.

    Returns:
        dict con 'score' (int 0-100) y 'breakdown' (aporte de cada criterio).
    """
    # Pesos: el nivel y el área son los filtros más importantes.
    weights = {
        "level": 30,
        "field": 25,
        "country": 10,
        "language": 15,
        "gpa": 10,
        "funding": 10,
    }
    breakdown = {
        "level": weights["level"] if level_matches else 0,
        "field": weights["field"] if field_matches else 0,
        "country": weights["country"] if country_matches else 0,
        "language": weights["language"] if language_ok else 0,
        "gpa": weights["gpa"] if gpa_ok else 0,
        "funding": weights["funding"] if covers_full_costs else 0,
    }
    return {"score": sum(breakdown.values()), "breakdown": breakdown}
