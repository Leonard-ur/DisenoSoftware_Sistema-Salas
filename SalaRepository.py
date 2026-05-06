from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from crear_db import Sala, Usuario, Asignacion, BloqueHorario, Seccion

#retorna todas las salas
def obtener_todas_las_salas(db: Session) -> list[Sala]:
    return db.query(Sala).order_by(Sala.codigo).all()

#retorna la sala según su id, retorna un mensaje de error si no existe
def obtener_sala_por_id(db: Session, sala_id: int) -> Sala:
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala:
        raise ValueError(f"No existe una sala con ID {sala_id}")
    return sala

#retorna la sala que sólo tenga el estado "DISPONIBLE"
def obtener_salas_disponibles(db: Session) -> list[Sala]:
    return (
        db.query(Sala)
        .filter(Sala.estado == "DISPONIBLE")
        .order_by(Sala.codigo)
        .all()
    )

#se le entrega los parámetros y devuelve las salas que cumplan con los requerimientos
def buscar_salas(
    db: Session,
    aforo: int,
    necesita_proyector: bool = False,
    necesita_enchufes: bool = False,
) -> list[Sala]:
    query = db.query(Sala).filter(
        Sala.estado == "DISPONIBLE",
        Sala.capacidad >= aforo,
    )

    if necesita_proyector:
        query = query.filter(Sala.proyector_ok == True)

    if necesita_enchufes:
        query = query.filter(Sala.enchufes_usables > 0)

    return query.order_by(Sala.capacidad).all()

#intenta insertar los datos, si no puede devuelve un mensaje de error
def guardar_solicitud(db: Session, seccion_id: int, sala_id: int, bloque_id: int, confirmado_por: int) -> Asignacion:
    asignacion = Asignacion(
        seccion_id=seccion_id,
        sala_id=sala_id,
        bloque_id=bloque_id,
        confirmado_por=confirmado_por,
        estado="CONFIRMADA",
    )
    try:
        db.add(asignacion)
        db.commit()
        db.refresh(asignacion)
        return asignacion
    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"La sala {sala_id} ya está ocupada en el bloque {bloque_id}. "
            "No se puede registrar la asignación."
        )

def obtener_todas_las_asignaciones(db: Session) -> list[Asignacion]:
    return (
        db.query(Asignacion)
        .filter(Asignacion.estado == "CONFIRMADA")
        .all()
    )

#intenta guardar datos de usuario, si ya hay un mail registrado develve un mensaje de error
def añadir_usuario(db: Session, nombre: str, email: str, rol: str) -> Usuario:
    roles_validos = {"DOCENTE", "COORDINADOR"}
    if rol not in roles_validos:
        raise ValueError(
            f"Rol '{rol}' no válido. Usa: {', '.join(roles_validos)}"
        )

    usuario = Usuario(nombre=nombre, email=email, rol=rol)
    try:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    except IntegrityError:
        db.rollback()
        raise ValueError(
            f"El mail '{email}' ya está registrado en el sistema."
        )

#retorna el usuario con el id entregado
def obtener_usuario_por_id(db: Session, usuario_id: int) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise ValueError(f"No existe un usuario con ID {usuario_id}")
    return usuario

#obtiene la id de los bloques con estado "CONFIRMADA" para después mostrar todos los bloques menos los obtenidos anteriormente
def obtener_bloque_disponible(db: Session, sala_id: int) -> list[BloqueHorario]:
    bloques_ocupados = (
        db.query(Asignacion.bloque_id)
        .filter(
            Asignacion.sala_id == sala_id,
            Asignacion.estado == "CONFIRMADA",
        )
        .subquery()
    )

    return (
        db.query(BloqueHorario)
        .filter(BloqueHorario.id.notin_(bloques_ocupados))
        .order_by(BloqueHorario.dia_semana, BloqueHorario.hora_inicio)
        .all()
    )

#obtiene todos los bloques
def obtener_todos_los_bloques(db: Session) -> list[BloqueHorario]:
    """Retorna todos los bloques horarios registrados."""
    return (
        db.query(BloqueHorario)
        .order_by(BloqueHorario.dia_semana, BloqueHorario.hora_inicio)
        .all()
    )
