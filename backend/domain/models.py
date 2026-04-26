"""
Entidades de dominio puras para el Sistema de Asignación de Salas.

Estas clases no dependen de ningún framework ni tecnología externa;
son el núcleo del modelo de negocio (Clean Architecture – Domain Layer).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Sala:
    """
    Representa una sala física disponible en la institución.

    Atributos:
        id:            Identificador único de la sala.
        nombre:        Nombre o código descriptivo (e.g. "Aula 3B").
        capacidad:     Número máximo de personas que puede alojar.
        equipamiento:  Lista de recursos técnicos disponibles
                       (e.g. ["proyector", "aire_acondicionado"]).
    """

    id: str
    nombre: str
    capacidad: int
    equipamiento: List[str] = field(default_factory=list)


@dataclass
class SolicitudAsignacion:
    """
    Representa una solicitud para reservar una sala en un horario dado.

    Atributos:
        id:                    Identificador único de la solicitud.
        alumnos_inscritos:     Número de alumnos que asistirán.
        inicio:                Fecha y hora de inicio de la clase/evento.
        fin:                   Fecha y hora de término de la clase/evento.
        equipamiento_requerido: Lista de recursos que la sala debe tener
                               (e.g. ["proyector"]).
        solicitante:           Nombre o identificador del docente/área
                               que hace la solicitud.
    """

    id: str
    alumnos_inscritos: int
    inicio: datetime
    fin: datetime
    equipamiento_requerido: List[str] = field(default_factory=list)
    solicitante: str = ""


@dataclass
class Asignacion:
    """
    Resultado de una asignación exitosa.

    Atributos:
        sala:      La sala asignada.
        solicitud: La solicitud que originó la asignación.
    """

    sala: Sala
    solicitud: SolicitudAsignacion
