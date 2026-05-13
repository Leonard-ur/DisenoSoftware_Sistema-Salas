# domain/entities.py

from dataclasses import dataclass
from typing import Optional
from datetime import time, datetime

@dataclass
class Sala:
    id: Optional[int]
    codigo: str
    capacidad: int
    estado: str
    proyector_ok: bool
    enchufes_usables: int

    def esta_disponible(self) -> bool:
        """Verifica si la sala no está en mantenimiento o ya asignada."""
        return self.estado == "DISPONIBLE"

    def cumple_requisitos(self, aforo_esperado: int, requiere_proyector: bool, requiere_enchufes: bool) -> bool:
        """
        Aplica las Reglas de Negocio (Business Rules):
        - BR-01 (Aforo): Capacidad >= aforo_esperado
        - BR-03 (Equipamiento): Validar proyector y enchufes si se requieren.
        """
        if self.capacidad < aforo_esperado:
            return False
        
        if requiere_proyector and not self.proyector_ok:
            return False
            
        if requiere_enchufes and self.enchufes_usables <= 0:
            return False
            
        return True

@dataclass
class Seccion:
    id: Optional[int]
    codigo: str
    aforo_inscrito: int
    necesita_proyector: bool
    necesita_enchufes: bool
    docente_id: int

@dataclass
class BloqueHorario:
    id: Optional[int]
    dia_semana: str
    hora_inicio: time
    hora_fin: time

@dataclass
class Usuario:
    id: Optional[int]
    nombre: str
    email: str
    rol: str

@dataclass
class Asignacion:
    id: Optional[int]
    seccion_id: int
    sala_id: int
    bloque_id: int
    estado: str
    confirmado_por: int
    creado_en: Optional[datetime] = None