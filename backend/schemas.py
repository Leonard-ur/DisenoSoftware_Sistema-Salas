from pydantic import BaseModel
from typing import List, Optional

#requisitos que el usuario envía para buscar una sala
class SolicitudSugerencia(BaseModel):
    bloque_id: int
    aforo_esperado: int
    necesita_proyector: bool
    necesita_enchufes: bool

#datos necesarios para confirmar una reserva
class ConfirmacionAsignacion(BaseModel):
    seccion_id: int
    sala_id: int
    bloque_id: int
    coordinador_id: int

#representación básica de una sala
class SalaResponse(BaseModel):
    id: int
    codigo: str 
    capacidad: int
    estado: str
    proyector_ok: bool
    enchufes_usables: int

    class Config:
        from_attributes = True

#respuesta que contiene la lista de recomendaciones
class SugerenciaResponse(BaseModel):
    mensaje: str
    salas_sugeridas: List[SalaResponse]

#confirmación básica de una asignación creada
class AsignacionResponse(BaseModel):
    id: int
    seccion_id: int
    sala_id: int
    bloque_id: int
    estado: str

    class Config:
        from_attributes = True

#información detallada de una asignación para el usuario final
class AsignacionDetalleResponse(BaseModel):
    id: int
    seccion_id: int
    sala_codigo: str
    sala_capacidad: int
    bloque_dia: str
    bloque_inicio: str
    bloque_fin: str
    estado: str
    creado_en: str

#representación de un bloque horario
class BloqueResponse(BaseModel):
    id: int
    dia_semana: str
    hora_inicio: str
    hora_fin: str

    class Config:
        from_attributes = True