# backend/main.py

from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException
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

app = FastAPI(title="Room Assignment API - Comando Estelar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")


# ==========================================
# DEPENDENCIES (composition root)
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


def get_room_request_repository(db: Session = Depends(get_db)) -> RoomRequestRepositorySQL:
    return RoomRequestRepositorySQL(db)


# ==========================================
# AUTH RESOURCES
# ==========================================


@router.post("/auth/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    return {
        "token": f"fake-jwt-token-{user.id}",
        "role": user.role,
        "name": user.name,
        "user_id": user.id
    }


# ==========================================
# ASSIGNMENT RESOURCES
# ==========================================


@router.post("/room-suggestions", response_model=schemas.RoomSuggestionResponse)
def create_room_suggestions(
    request: schemas.RoomSuggestionRequest,
    use_case: AssignmentUseCase = Depends(get_assignment_use_case),
):
    rooms = use_case.suggest_optimal_rooms(
        time_block_id=request.time_block_id,
        expected_attendance=request.expected_attendance,
        requires_projector=request.requires_projector,
        requires_outlets=request.requires_outlets,
    )
    if not rooms:
        return {
            "message": "No rooms match the given requirements.",
            "suggested_rooms": [],
        }
    return {"message": "Rooms found successfully.", "suggested_rooms": rooms}


@router.post("/assignments", response_model=schemas.AssignmentResponse)
def create_assignment(
    request: schemas.AssignmentRequest,
    use_case: AssignmentUseCase = Depends(get_assignment_use_case),
):
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
)
def list_assignments(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
):
    return use_case.list_teacher_assignments()


@router.get("/requests", response_model=List[schemas.RoomRequestSchema])
def list_room_requests(
    repository: RoomRequestRepositorySQL = Depends(get_room_request_repository),
):
    return repository.get_pending_requests()


# ==========================================
# DASHBOARD AND ROOM RESOURCES
# ==========================================


@router.get("/statistics")
def get_statistics(
    use_case: DashboardUseCase = Depends(get_dashboard_use_case),
):
    return use_case.get_general_statistics()


@router.get("/rooms", response_model=List[schemas.RoomResponse])
def list_rooms(repository: RoomRepositorySQL = Depends(get_room_repository)):
    return repository.get_all_rooms()


app.include_router(router)
