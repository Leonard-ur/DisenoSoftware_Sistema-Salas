# backend/main.py

from typing import List, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import schemas
from infrastructure.database import SessionLocal, User
from infrastructure.repository import (
    AssignmentRepositorySQL,
    RoomRepositorySQL,
    RoomRequestRepositorySQL,
    TimeBlockRepositorySQL,
)
from use_cases.assignment import AssignmentUseCase
from use_cases.dashboard import DashboardUseCase

app = FastAPI(
    title="Sistema de Asignación de Salas",
    description=(
        "API para gestionar salas universitarias: "
        "búsqueda por requisitos técnicos, asignaciones y panel de control."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")


# ==========================================
# DEPENDENCIES
# ==========================================


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_assignment_use_case(
    db: Session = Depends(get_db),
) -> AssignmentUseCase:
    return AssignmentUseCase(
        RoomRepositorySQL(db),
        AssignmentRepositorySQL(db),
        TimeBlockRepositorySQL(db),
    )


def get_dashboard_use_case(
    db: Session = Depends(get_db),
) -> DashboardUseCase:
    return DashboardUseCase(RoomRepositorySQL(db), AssignmentRepositorySQL(db))


def get_room_repository(db: Session = Depends(get_db)) -> RoomRepositorySQL:
    return RoomRepositorySQL(db)


def get_room_request_repository(
    db: Session = Depends(get_db),
) -> RoomRequestRepositorySQL:
    return RoomRequestRepositorySQL(db)


def get_time_block_repository(
    db: Session = Depends(get_db),
) -> TimeBlockRepositorySQL:
    return TimeBlockRepositorySQL(db)


# ==========================================
# AUTH
# ==========================================


@router.post(
    "/auth/login",
    response_model=schemas.LoginResponse,
    tags=["Auth"],
    summary="Iniciar sesión",
)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Autentica un usuario (DOCENTE o COORDINADOR) y retorna su rol e id."""
    user = db.query(User).filter(User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {
        "token": f"fake-jwt-token-{user.id}",
        "role": user.role,
        "name": user.name,
        "user_id": user.id,
    }


# ==========================================
# ROOMS
# ==========================================


@router.get(
    "/rooms",
    response_model=List[schemas.RoomResponse],
    tags=["Salas"],
    summary="Listar todas las salas",
)
def list_rooms(
    repository: RoomRepositorySQL = Depends(get_room_repository),
):
    """Retorna el inventario completo de salas con todos sus atributos."""
    return repository.get_all_rooms()


@router.get(
    "/rooms/available",
    response_model=List[schemas.RoomResponse],
    tags=["Salas"],
    summary="Listar salas disponibles",
)
def list_available_rooms(
    repository: RoomRepositorySQL = Depends(get_room_repository),
):
    """Retorna solo las salas con estado DISPONIBLE."""
    return repository.get_available_rooms()


@router.get(
    "/rooms/filter",
    response_model=List[schemas.RoomResponse],
    tags=["Salas"],
    summary="Filtrar salas por atributos",
    description=(
        "Filtra el inventario por cualquier combinación de atributos: "
        "estado, proyector, enchufes, accesibilidad, tag y aforo mínimo. "
        "Todos los parámetros son opcionales."
    ),
)
def filter_rooms(
    status: Optional[str] = Query(
        None,
        description="DISPONIBLE | ASIGNADA | MANTENIMIENTO",
    ),
    has_projector: Optional[bool] = Query(
        None, description="True si la sala debe tener proyector"
    ),
    requires_outlets: Optional[bool] = Query(
        None, description="True si la sala debe tener enchufes operativos"
    ),
    is_accessible: Optional[bool] = Query(
        None, description="True si la sala debe cumplir accesibilidad universal"
    ),
    tags: Optional[str] = Query(
        None, description="Tag de categoría, e.g. 'computacion'"
    ),
    min_capacity: Optional[int] = Query(
        None, description="Aforo físico mínimo requerido"
    ),
    repository: RoomRepositorySQL = Depends(get_room_repository),
):
    rooms = repository.get_all_rooms()
    if status is not None:
        rooms = [r for r in rooms if r.status == status]
    if has_projector is not None:
        rooms = [r for r in rooms if r.has_projector == has_projector]
    if requires_outlets:
        rooms = [r for r in rooms if r.usable_outlets > 0]
    if is_accessible is not None:
        rooms = [r for r in rooms if r.is_accessible == is_accessible]
    if tags is not None:
        rooms = [
            r for r in rooms if r.tags and tags.lower() in r.tags.lower()
        ]
    if min_capacity is not None:
        rooms = [r for r in rooms if r.capacity >= min_capacity]
    return rooms


@router.get(
    "/rooms/{room_id}",
    response_model=schemas.RoomResponse,
    tags=["Salas"],
    summary="Obtener sala por ID",
)
def get_room(
    room_id: int,
    repository: RoomRepositorySQL = Depends(get_room_repository),
):
    """Retorna el detalle completo de una sala específica."""
    try:
        return repository.get_room_by_id(room_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


# ==========================================
# ROOM REQUESTS (solicitudes de docentes)
# ==========================================


@router.post(
    "/requests",
    response_model=schemas.RoomRequestResponse,
    tags=["Solicitudes"],
    summary="Crear solicitud de sala (Docente)",
    status_code=201,
)
def create_room_request(
    body: schemas.RoomRequestCreate,
    repository: RoomRequestRepositorySQL = Depends(get_room_request_repository),
):
    """
    El docente envía los requisitos de su clase (aforo, proyector, enchufes,
    accesibilidad y bloque horario deseado). La solicitud queda en estado
    PENDIENTE hasta que un coordinador la gestione.
    """
    return repository.create_request(
        teacher_id=body.teacher_id,
        course_name=body.course_name,
        expected_attendance=body.expected_attendance,
        requires_projector=body.requires_projector,
        requires_outlets=body.requires_outlets,
        requires_accessibility=body.requires_accessibility,
        time_block_id=body.time_block_id,
    )


@router.get(
    "/requests",
    response_model=List[schemas.RoomRequestResponse],
    tags=["Solicitudes"],
    summary="Listar solicitudes pendientes (Coordinador)",
)
def list_pending_requests(
    repository: RoomRequestRepositorySQL = Depends(get_room_request_repository),
):
    """Retorna todas las solicitudes en estado PENDIENTE para que el coordinador las gestione."""
    return repository.get_pending_requests()


@router.get(
    "/requests/teacher/{teacher_id}",
    response_model=List[schemas.RoomRequestResponse],
    tags=["Solicitudes"],
    summary="Solicitudes de un docente",
)
def list_requests_by_teacher(
    teacher_id: int,
    repository: RoomRequestRepositorySQL = Depends(get_room_request_repository),
):
    """Retorna todas las solicitudes de un docente específico (historial)."""
    return repository.get_requests_by_teacher(teacher_id)


@router.patch(
    "/requests/{request_id}/status",
    response_model=schemas.RoomRequestResponse,
    tags=["Solicitudes"],
    summary="Aprobar o rechazar una solicitud (Coordinador)",
)
def update_request_status(
    request_id: int,
    body: schemas.RoomRequestStatusUpdate,
    repository: RoomRequestRepositorySQL = Depends(get_room_request_repository),
):
    """
    El coordinador cambia el estado de una solicitud a APROBADA o RECHAZADA.
    """
    valid = {"APROBADA", "RECHAZADA"}
    if body.status not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Use: {', '.join(sorted(valid))}",
        )
    try:
        return repository.update_status(request_id, body.status)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


# ==========================================
# ROOM SUGGESTIONS (motor de búsqueda)
# ==========================================


@router.post(
    "/room-suggestions",
    response_model=schemas.RoomSuggestionResponse,
    tags=["Búsqueda de Salas"],
    summary="Buscar salas que cumplan requisitos técnicos",
    description=(
        "Motor de búsqueda por restricciones: recibe los requisitos de una "
        "sección y retorna las salas disponibles ordenadas por eficiencia."
    ),
)
def create_room_suggestions(
    request: schemas.RoomSuggestionRequest,
    use_case: AssignmentUseCase = Depends(get_assignment_use_case),
):
    rooms = use_case.suggest_optimal_rooms(
        time_block_id=request.time_block_id,
        expected_attendance=request.expected_attendance,
        requires_projector=request.requires_projector,
        requires_outlets=request.requires_outlets,
        requires_accessibility=request.requires_accessibility,
        required_tags=request.required_tags,
    )
    if not rooms:
        return {
            "message": "No se encontraron salas que cumplan los requisitos.",
            "suggested_rooms": [],
        }
    return {
        "message": f"{len(rooms)} sala(s) encontrada(s).",
        "suggested_rooms": rooms,
    }


# ==========================================
# ASSIGNMENTS
# ==========================================


@router.post(
    "/assignments",
    response_model=schemas.AssignmentResponse,
    tags=["Asignaciones"],
    summary="Confirmar asignación de sala (Coordinador)",
)
def create_assignment(
    request: schemas.AssignmentRequest,
    use_case: AssignmentUseCase = Depends(get_assignment_use_case),
):
    """El coordinador confirma la asignación de una sala a una sección."""
    try:
        return use_case.confirm_assignment(
            section_id=request.section_id,
            room_id=request.room_id,
            time_block_id=request.time_block_id,
            coordinator_id=request.coordinator_id,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/assignments",
    response_model=List[schemas.AssignmentDetailResponse],
    tags=["Asignaciones"],
    summary="Listar asignaciones confirmadas",
)
def list_assignments(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
):
    """Retorna el historial de asignaciones con detalle de sala y bloque."""
    return use_case.list_teacher_assignments()


# ==========================================
# TIME BLOCKS
# ==========================================


@router.get(
    "/time-blocks",
    response_model=List[schemas.TimeBlockResponse],
    tags=["Bloques Horarios"],
    summary="Listar todos los bloques horarios",
)
def list_time_blocks(
    repository: TimeBlockRepositorySQL = Depends(get_time_block_repository),
):
    """Retorna todos los bloques horarios disponibles en el sistema."""
    return repository.get_all_blocks()


@router.get(
    "/time-blocks/available/{room_id}",
    response_model=List[schemas.TimeBlockResponse],
    tags=["Bloques Horarios"],
    summary="Bloques horarios libres para una sala",
)
def list_available_blocks_for_room(
    room_id: int,
    repository: TimeBlockRepositorySQL = Depends(get_time_block_repository),
):
    """Retorna los bloques en que una sala específica no está ocupada."""
    return repository.get_available_blocks(room_id)


# ==========================================
# DASHBOARD
# ==========================================


@router.get(
    "/statistics",
    tags=["Dashboard"],
    summary="Estadísticas generales del sistema",
)
def get_statistics(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
):
    """Conteos de salas por estado, porcentaje de ocupación y total de asignaciones."""
    return use_case.get_general_statistics()


app.include_router(router)
