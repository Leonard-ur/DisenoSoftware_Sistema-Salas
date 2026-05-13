# backend/schemas.py

from pydantic import BaseModel
from typing import List, Optional # sirve para indicar que un campo puede ser opcional, no se esta utilizando en este proyecto pero es buena practica importarlo por si se necesita en el futuro

# ==========================================
# ESQUEMAS DE ENTRADA (Lo que envía el Frontend)
# ==========================================

class SolicitudSugerencia(BaseModel):
    """
    Datos que envía el Coordinador/Profesor para pedirle al motor 
    que sugiera las mejores salas.
    """
    bloque_id: int
    aforo_esperado: int
    necesita_proyector: bool
    necesita_enchufes: bool

class ConfirmacionAsignacion(BaseModel):
    """
    Datos que envía el Coordinador cuando hace clic en "Asignar Sala".
    """
    seccion_id: int
    sala_id: int
    bloque_id: int
    coordinador_id: int


# ==========================================
# ESQUEMAS DE SALIDA (Lo que responde la API)
# ==========================================

class SalaResponse(BaseModel):
    """
    Estructura de los datos de la Sala que se enviarán al Frontend.
    """
    id: int
    codigo: str
    capacidad: int
    estado: str
    proyector_ok: bool
    enchufes_usables: int

    class Config:
        from_attributes = True  # Permite leer datos de objetos de Python/SQLAlchemy

class SugerenciaResponse(BaseModel):
    """
    Respuesta que agrupa la lista de salas sugeridas por el motor.
    """
    mensaje: str
    salas_sugeridas: List[SalaResponse]

class AsignacionResponse(BaseModel):
    """
    Respuesta cuando una asignación se confirma exitosamente.
    """
    id: int
    seccion_id: int
    sala_id: int
    bloque_id: int
    estado: str

    class Config:
        from_attributes = True