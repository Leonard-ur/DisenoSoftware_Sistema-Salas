# domain/entities.py

from dataclasses import dataclass
from typing import Optional
from datetime import time, datetime
import math

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

    def capacidad_efectiva(self) -> int:
        """
        BR-01 (Aforo Legal y Sanitario): 
        La capacidad real permitida es el 95% de la capacidad física.
        Usamos math.floor para redondear hacia abajo por seguridad 
        (ej: 41 * 0.95 = 38.95 -> 38 asientos reales).
        """
        return math.floor(self.capacidad * 0.95)

    def cumple_requisitos(self, aforo_esperado: int, requiere_proyector: bool, requiere_enchufes: bool) -> bool:
        """
        Aplica las Reglas de Negocio (Business Rules):
        - BR-01 (Aforo): Capacidad efectiva >= aforo_esperado
        - BR-03 (Equipamiento): Validar proyector y enchufes si se requieren.
        """
        if self.capacidad_efectiva() < aforo_esperado:
            return False
        
        if requiere_proyector and not self.proyector_ok:
            return False
            
        if requiere_enchufes and self.enchufes_usables <= 0:
            return False
            
        return True

    def calcular_score_eficiencia(self, aforo_esperado: int) -> int:
        """
        FR-04 (Sugerencia Óptima): Calcula los asientos sobrantes.
        Un menor score significa una mayor eficiencia (menos desperdicio de espacio).
        """
        return self.capacidad_efectiva() - aforo_esperado

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