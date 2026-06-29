"""Guardrails deterministas (defense-in-depth, capa 1).

Estas funciones NO usan IA: son reglas rígidas en código para detectar entradas
maliciosas ANTES de que lleguen al modelo. Complementan (no reemplazan) las
instrucciones defensivas que ya pusimos en cada agente.

Mitigan principalmente:
- Prompt injection: intentos de anular las instrucciones del sistema.
- Tamaño excesivo: entradas enormes que disparan costo/latencia.
"""

from __future__ import annotations

import re

# Patrones típicos de inyección de prompts. Lista no exhaustiva pero efectiva
# como primera barrera. Se comparan en minúsculas.
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore (all|the|your|previous|above) (instructions|rules)",
        r"ignora (todas|tus|las) (instrucciones|reglas)",
        r"disregard (the|your|all|previous) ",
        r"forget (your|the|all|previous) (instructions|rules|prompt)",
        r"you are now ",
        r"act as (an|a) ",
        r"system prompt",
        r"reveal (your|the) (system )?(prompt|instructions)",
        r"developer mode",
        r"jailbreak",
    )
)

# Límite de longitud de la entrada del usuario (caracteres).
MAX_INPUT_CHARS = 4000


def detect_injection(text: str) -> list[str]:
    """Devuelve la lista de patrones de inyección detectados (vacía si no hay)."""
    return [p.pattern for p in _INJECTION_PATTERNS if p.search(text)]


def sanitize_user_input(text: str) -> str:
    """Limpia la entrada del usuario antes de pasarla a los agentes.

    - Recorta a MAX_INPUT_CHARS para acotar costo y superficie de ataque.
    - Colapsa espacios en blanco redundantes.
    No "censura" el contenido: la neutralización de instrucciones la refuerzan
    las propias instrucciones de los agentes (tratar input como datos).
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:MAX_INPUT_CHARS]


def is_safe_input(text: str) -> tuple[bool, str]:
    """Valida la entrada. Devuelve (es_segura, motivo).

    El motivo sirve para registrar (sin exponer PII) por qué se rechazó.
    """
    if not text or not text.strip():
        return False, "entrada vacía"
    hits = detect_injection(text)
    if hits:
        return False, f"posible prompt injection ({len(hits)} patrón/es)"
    return True, "ok"
