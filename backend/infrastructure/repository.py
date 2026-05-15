import sys
import os
# Esto le dice a Python que la carpeta raíz del proyecto es la que está un nivel más arriba.
# Así podrá encontrar las carpetas 'domain', 'use_cases', etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# 1. Importamos los modelos de la Base de Datos de Lucas (con alias para no confundir)
from infrastructure.crear_db import (
    Sala as SalaDB, 
    Usuario as UsuarioDB, 
    Asignacion as AsignacionDB, 
    BloqueHorario as BloqueHorarioDB, 
    Seccion as SeccionDB
)

# 2. Importamos las Entidades puras y los Puertos de Camilo
from domain.entities import Sala, Usuario, Asignacion, BloqueHorario
from domain.ports import (
    ISalaRepository, 
    IAsignacionRepository, 
    IUsuarioRepository, 
    IBloqueHorarioRepository
)

# ==========================================
# MAPPERS (Traductores de DB a Entidad Pura)
# ==========================================
def map_sala_to_entity(sala_db: SalaDB) -> Optional[Sala]:
    if not sala_db: return None
    return Sala(
        id=sala_db.id,
        codigo=sala_db.codigo,
        capacidad=sala_db.capacidad,
        estado=sala_db.estado,
        proyector_ok=sala_db.proyector_ok,
        enchufes_usables=sala_db.enchufes_usables
    )

def map_asignacion_to_entity(asig_db: AsignacionDB) -> Optional[Asignacion]:
    if not asig_db: return None
    return Asignacion(
        id=asig_db.id,
        seccion_id=asig_db.seccion_id,
        sala_id=asig_db.sala_id,
        bloque_id=asig_db.bloque_id,
        estado=asig_db.estado,
        confirmado_por=asig_db.confirmado_por,
        creado_en=asig_db.creado_en
    )

def map_usuario_to_entity(user_db: UsuarioDB) -> Optional[Usuario]:
    if not user_db: return None
    return Usuario(
        id=user_db.id,
        nombre=user_db.nombre,
        email=user_db.email,
        rol=user_db.rol
    )

def map_bloque_to_entity(bloque_db: BloqueHorarioDB) -> Optional[BloqueHorario]:
    if not bloque_db: return None
    return BloqueHorario(
        id=bloque_db.id,
        dia_semana=bloque_db.dia_semana,
        hora_inicio=bloque_db.hora_inicio,
        hora_fin=bloque_db.hora_fin
    )


# ==========================================
# REPOSITORIOS (Implementación de los Puertos)
# ==========================================

class SalaRepositorySQL(ISalaRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_todas_las_salas(self) -> List[Sala]:
        salas_db = self.db.query(SalaDB).order_by(SalaDB.codigo).all()
        return [map_sala_to_entity(s) for s in salas_db]

    def obtener_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        sala_db = self.db.query(SalaDB).filter(SalaDB.id == sala_id).first()
        if not sala_db:
            raise ValueError(f"No existe una sala con ID {sala_id}")
        return map_sala_to_entity(sala_db)

    def obtener_salas_disponibles(self) -> List[Sala]:
        salas_db = self.db.query(SalaDB).filter(SalaDB.estado == "DISPONIBLE").order_by(SalaDB.codigo).all()
        return [map_sala_to_entity(s) for s in salas_db]

    def buscar_salas(self, aforo: int, necesita_proyector: bool, necesita_enchufes: bool) -> List[Sala]:
        query = self.db.query(SalaDB).filter(SalaDB.estado == "DISPONIBLE", SalaDB.capacidad >= aforo)
        if necesita_proyector:
            query = query.filter(SalaDB.proyector_ok == True)
        if necesita_enchufes:
            query = query.filter(SalaDB.enchufes_usables > 0)
        
        salas_db = query.order_by(SalaDB.capacidad).all()
        return [map_sala_to_entity(s) for s in salas_db]


class AsignacionRepositorySQL(IAsignacionRepository):
    def __init__(self, db: Session):
        self.db = db

    def guardar_solicitud(self, seccion_id: int, sala_id: int, bloque_id: int, confirmado_por: int) -> Asignacion:
        asignacion_db = AsignacionDB(
            seccion_id=seccion_id,
            sala_id=sala_id,
            bloque_id=bloque_id,
            confirmado_por=confirmado_por,
            estado="CONFIRMADA",
        )
        try:
            self.db.add(asignacion_db)
            self.db.commit()
            self.db.refresh(asignacion_db)
            return map_asignacion_to_entity(asignacion_db)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"La sala {sala_id} ya está ocupada en el bloque {bloque_id}. No se puede registrar la asignación.")

    def obtener_todas_las_asignaciones(self) -> List[Asignacion]:
        asig_db = self.db.query(AsignacionDB).filter(AsignacionDB.estado == "CONFIRMADA").all()
        return [map_asignacion_to_entity(a) for a in asig_db]

    def obtener_asignaciones_detalladas(self) -> List[dict]:
        # Aquí SÍ es legal usar SQLAlchemy, porque estamos en la capa de Infraestructura
        asignaciones = (
            self.db.query(AsignacionDB)
            .filter(AsignacionDB.estado == "CONFIRMADA")
            .order_by(AsignacionDB.creado_en.desc())
            .all()
        )

        result = []
        for a in asignaciones:
            result.append({
                "id": a.id,
                "seccion_id": a.seccion_id,
                "sala_codigo": a.sala.codigo if a.sala else f"#{a.sala_id}",
                "sala_capacidad": a.sala.capacidad if a.sala else 0,
                "bloque_dia": a.bloque.dia_semana if a.bloque else "—",
                "bloque_inicio": str(a.bloque.hora_inicio)[:5] if a.bloque else "—",
                "bloque_fin": str(a.bloque.hora_fin)[:5] if a.bloque else "—",
                "estado": a.estado,
                "creado_en": a.creado_en.strftime("%d/%m/%Y %H:%M") if a.creado_en else "—",
            })
        return result


class UsuarioRepositorySQL(IUsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def añadir_usuario(self, nombre: str, email: str, rol: str) -> Usuario:
        roles_validos = {"DOCENTE", "COORDINADOR"}
        if rol not in roles_validos:
            raise ValueError(f"Rol '{rol}' no válido. Usa: {', '.join(roles_validos)}")

        usuario_db = UsuarioDB(nombre=nombre, email=email, rol=rol)
        try:
            self.db.add(usuario_db)
            self.db.commit()
            self.db.refresh(usuario_db)
            return map_usuario_to_entity(usuario_db)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"El mail '{email}' ya está registrado en el sistema.")

    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]:
        user_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
        if not user_db:
            raise ValueError(f"No existe un usuario con ID {usuario_id}")
        return map_usuario_to_entity(user_db)


class BloqueHorarioRepositorySQL(IBloqueHorarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_bloque_disponible(self, sala_id: int) -> List[BloqueHorario]:
        bloques_ocupados = (
            self.db.query(AsignacionDB.bloque_id)
            .filter(AsignacionDB.sala_id == sala_id, AsignacionDB.estado == "CONFIRMADA")
            .subquery()
        )
        bloques_db = (
            self.db.query(BloqueHorarioDB)
            .filter(BloqueHorarioDB.id.notin_(bloques_ocupados))
            .order_by(BloqueHorarioDB.dia_semana, BloqueHorarioDB.hora_inicio)
            .all()
        )
        return [map_bloque_to_entity(b) for b in bloques_db]

    def obtener_todos_los_bloques(self) -> List[BloqueHorario]:
        bloques_db = self.db.query(BloqueHorarioDB).order_by(BloqueHorarioDB.dia_semana, BloqueHorarioDB.hora_inicio).all()
        return [map_bloque_to_entity(b) for b in bloques_db]