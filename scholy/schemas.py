"""Modelos de datos (pydantic) que estructuran la información del sistema.

Estos esquemas cumplen dos funciones clave:
1. Definen el "contrato" de datos entre el frontend, los agentes y la API.
2. Permiten salidas estructuradas y validadas (menos alucinaciones, más control).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AcademicLevel(str, Enum):
    """Nivel académico objetivo. Es la variable que dirige toda la búsqueda."""

    pregrado = "pregrado"
    posgrado = "posgrado"  # maestría / máster
    doctorado = "doctorado"
    otro = "otro"


class StudyMode(str, Enum):
    """Modalidad preferida de estudio."""

    presencial = "presencial"
    hibrida = "hibrida"
    online = "online"
    indiferente = "indiferente"


class StudentProfile(BaseModel):
    """Perfil del estudiante. Entrada principal del sistema.

    Solo ``academic_level`` y ``field_of_study`` son obligatorios; el resto es
    opcional para no bloquear a quien aún no tiene todo definido (p. ej. país).
    """

    # --- Variables principales (dirigen la búsqueda) ---
    academic_level: AcademicLevel = Field(
        ..., description="Nivel de la beca buscada: pregrado, posgrado, doctorado u otro."
    )
    field_of_study: str = Field(
        ..., description="Área de estudio, p. ej. 'ingeniería de software', 'medicina'."
    )

    # --- Variables de segmentación (opcionales) ---
    target_country: str | None = Field(
        default=None,
        description="País deseado. Vacío/None = sin preferencia (búsqueda global).",
    )
    nationality: str | None = Field(
        default=None,
        description="Nacionalidad del estudiante. Clave porque muchas becas la restringen.",
    )
    certified_languages: list[str] = Field(
        default_factory=list,
        description="Idiomas certificados, p. ej. ['inglés (IELTS 7.0)', 'danés (nativo)'].",
    )

    # --- Condiciones y restricciones ---
    has_extra_income: bool = Field(
        default=False,
        description="True si el estudiante cuenta con ingreso extra para manutención.",
    )
    needs_full_funding: bool = Field(
        default=True,
        description="True si necesita que la beca cubra matrícula + manutención (no solo matrícula).",
    )
    gpa: float | None = Field(
        default=None,
        ge=0,
        description="Promedio académico (escala libre). Algunas becas piden un mínimo.",
    )
    study_mode: StudyMode = Field(
        default=StudyMode.indiferente, description="Modalidad preferida de estudio."
    )
    notes: str | None = Field(
        default=None, description="Notas libres adicionales del estudiante."
    )


class Scholarship(BaseModel):
    """Una beca encontrada y analizada."""

    name: str = Field(..., description="Nombre de la beca o programa.")
    institution: str | None = Field(default=None, description="Universidad u organismo que la otorga.")
    country: str | None = Field(default=None, description="País donde aplica la beca.")
    academic_level: str | None = Field(default=None, description="Nivel que cubre la beca.")
    coverage: str | None = Field(
        default=None,
        description="Qué cubre: 'completa', 'solo matrícula', 'matrícula + estipendio', etc.",
    )
    language_requirement: str | None = Field(
        default=None, description="Requisito de idioma, p. ej. 'IELTS 6.5' o 'danés'."
    )
    eligibility_notes: str | None = Field(
        default=None, description="Restricciones de nacionalidad, GPA u otros requisitos."
    )
    deadline: str | None = Field(default=None, description="Fecha límite, si se conoce.")
    url: str | None = Field(default=None, description="Enlace oficial de la beca.")

    # Campos calculados por el AdvisorAgent / la herramienta de compatibilidad.
    match_score: int | None = Field(
        default=None, ge=0, le=100, description="Puntaje de compatibilidad 0-100."
    )
    financial_fit: str | None = Field(
        default=None, description="Resumen del encaje financiero para este estudiante."
    )


class Recommendation(BaseModel):
    """Salida final del sistema: lista de becas recomendadas + resumen."""

    summary: str = Field(..., description="Resumen breve y accionable para el estudiante.")
    scholarships: list[Scholarship] = Field(
        default_factory=list, description="Becas recomendadas, idealmente ordenadas por match_score."
    )
