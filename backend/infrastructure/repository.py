# infrastructure/repository.py

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities import Assignment, Room, RoomRequest, TimeBlock, User
from domain.ports import (
    IAssignmentRepository,
    IRoomRepository,
    IRoomRequestRepository,
    ITimeBlockRepository,
    IUserRepository,
)
from infrastructure.database import Assignment as AssignmentModel
from infrastructure.database import Room as RoomModel
from infrastructure.database import RoomRequest as RoomRequestModel
from infrastructure.database import TimeBlock as TimeBlockModel
from infrastructure.database import User as UserModel

# ==========================================
# MAPPERS
# ==========================================


def _map_room(model: Optional[RoomModel]) -> Optional[Room]:
    if model is None:
        return None
    return Room(
        id=model.id,
        code=model.code,
        capacity=model.capacity,
        status=model.status,
        has_projector=model.has_projector,
        usable_outlets=model.usable_outlets,
        is_accessible=model.is_accessible,
        tags=model.tags,
    )


def _map_room_request(
    model: Optional[RoomRequestModel],
) -> Optional[RoomRequest]:
    if model is None:
        return None
    return RoomRequest(
        id=model.id,
        teacher_id=model.teacher_id,
        course_name=model.course_name,
        expected_attendance=model.expected_attendance,
        requires_projector=model.requires_projector,
        requires_outlets=model.requires_outlets,
        requires_accessibility=model.requires_accessibility,
        time_block_id=model.time_block_id,
        status=model.status,
        created_at=model.created_at,
    )


def _map_assignment(model: Optional[AssignmentModel]) -> Optional[Assignment]:
    if model is None:
        return None
    return Assignment(
        id=model.id,
        section_id=model.section_id,
        room_id=model.room_id,
        time_block_id=model.time_block_id,
        status=model.status,
        confirmed_by=model.confirmed_by,
        created_at=model.created_at,
    )


def _map_user(model: Optional[UserModel]) -> Optional[User]:
    if model is None:
        return None
    return User(
        id=model.id,
        name=model.name,
        email=model.email,
        role=model.role,
    )


def _map_time_block(model: Optional[TimeBlockModel]) -> Optional[TimeBlock]:
    if model is None:
        return None
    return TimeBlock(
        id=model.id,
        weekday=model.weekday,
        start_time=model.start_time,
        end_time=model.end_time,
    )


def _to_request_dict(model: RoomRequestModel) -> dict:
    """Build the read model for a single room request."""
    teacher = model.teacher
    block = model.time_block
    return {
        "id": model.id,
        "teacher_id": model.teacher_id,
        "teacher_name": teacher.name if teacher else f"#{model.teacher_id}",
        "course_name": model.course_name,
        "expected_attendance": model.expected_attendance,
        "requires_projector": model.requires_projector,
        "requires_outlets": model.requires_outlets,
        "requires_accessibility": model.requires_accessibility,
        "time_block_id": model.time_block_id,
        "time_block_day": block.weekday if block else None,
        "time_block_start": str(block.start_time)[:5] if block else None,
        "time_block_end": str(block.end_time)[:5] if block else None,
        "status": model.status,
        "created_at": (
            model.created_at.strftime("%d/%m/%Y %H:%M")
            if model.created_at
            else None
        ),
    }


def _to_detail_dict(model: AssignmentModel) -> dict:
    """Build the cross-referenced read model for a single assignment."""
    room = model.room
    block = model.time_block
    return {
        "id": model.id,
        "section_id": model.section_id,
        "room_code": room.code if room else f"#{model.room_id}",
        "room_capacity": room.capacity if room else 0,
        "time_block_day": block.weekday if block else "—",
        "time_block_start": str(block.start_time)[:5] if block else "—",
        "time_block_end": str(block.end_time)[:5] if block else "—",
        "status": model.status,
        "created_at": (
            model.created_at.strftime("%d/%m/%Y %H:%M")
            if model.created_at
            else "—"
        ),
    }


# ==========================================
# REPOSITORIES
# ==========================================


class RoomRepositorySQL(IRoomRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all_rooms(self) -> List[Room]:
        rows = self.db.query(RoomModel).order_by(RoomModel.code).all()
        return [_map_room(row) for row in rows]

    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        row = self.db.query(RoomModel).filter(RoomModel.id == room_id).first()
        if row is None:
            raise ValueError(f"Room with id {room_id} does not exist")
        return _map_room(row)

    def get_available_rooms(self) -> List[Room]:
        rows = (
            self.db.query(RoomModel)
            .filter(RoomModel.status == "DISPONIBLE")
            .order_by(RoomModel.code)
            .all()
        )
        return [_map_room(row) for row in rows]

    def search_rooms(
        self,
        attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
    ) -> List[Room]:
        query = self.db.query(RoomModel).filter(
            RoomModel.status == "DISPONIBLE",
            RoomModel.capacity >= attendance,
        )
        if requires_projector:
            query = query.filter(RoomModel.has_projector.is_(True))
        if requires_outlets:
            query = query.filter(RoomModel.usable_outlets > 0)
        rows = query.order_by(RoomModel.capacity).all()
        return [_map_room(row) for row in rows]


class RoomRequestRepositorySQL(IRoomRequestRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_request(
        self,
        teacher_id: int,
        course_name: str,
        expected_attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
        requires_accessibility: bool,
        time_block_id: Optional[int],
    ) -> RoomRequest:
        model = RoomRequestModel(
            teacher_id=teacher_id,
            course_name=course_name,
            expected_attendance=expected_attendance,
            requires_projector=requires_projector,
            requires_outlets=requires_outlets,
            requires_accessibility=requires_accessibility,
            time_block_id=time_block_id,
            status="PENDIENTE",
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _map_room_request(model)

    def get_pending_requests(self) -> List[dict]:
        rows = (
            self.db.query(RoomRequestModel)
            .filter(RoomRequestModel.status == "PENDIENTE")
            .order_by(RoomRequestModel.created_at.desc())
            .all()
        )
        return [_to_request_dict(row) for row in rows]

    def get_requests_by_teacher(self, teacher_id: int) -> List[dict]:
        rows = (
            self.db.query(RoomRequestModel)
            .filter(RoomRequestModel.teacher_id == teacher_id)
            .order_by(RoomRequestModel.created_at.desc())
            .all()
        )
        return [_to_request_dict(row) for row in rows]

    def update_status(self, request_id: int, status: str) -> RoomRequest:
        model = (
            self.db.query(RoomRequestModel)
            .filter(RoomRequestModel.id == request_id)
            .first()
        )
        if model is None:
            raise ValueError(f"RoomRequest with id {request_id} does not exist")
        model.status = status
        self.db.commit()
        self.db.refresh(model)
        return _map_room_request(model)


class AssignmentRepositorySQL(IAssignmentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_request(
        self,
        section_id: int,
        room_id: int,
        time_block_id: int,
        confirmed_by: int,
    ) -> Assignment:
        model = AssignmentModel(
            section_id=section_id,
            room_id=room_id,
            time_block_id=time_block_id,
            confirmed_by=confirmed_by,
            status="CONFIRMADA",
        )
        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return _map_assignment(model)
        except IntegrityError as error:
            self.db.rollback()
            raise ValueError(
                f"Room {room_id} is already booked for time block "
                f"{time_block_id}; the assignment cannot be registered."
            ) from error

    def get_all_assignments(self) -> List[Assignment]:
        rows = (
            self.db.query(AssignmentModel)
            .filter(AssignmentModel.status == "CONFIRMADA")
            .all()
        )
        return [_map_assignment(row) for row in rows]

    def get_detailed_assignments(self) -> List[dict]:
        rows = (
            self.db.query(AssignmentModel)
            .filter(AssignmentModel.status == "CONFIRMADA")
            .order_by(AssignmentModel.created_at.desc())
            .all()
        )
        return [_to_detail_dict(row) for row in rows]


class UserRepositorySQL(IUserRepository):
    VALID_ROLES = {"DOCENTE", "COORDINADOR"}

    def __init__(self, db: Session):
        self.db = db

    def add_user(self, name: str, email: str, role: str) -> User:
        if role not in self.VALID_ROLES:
            valid = ", ".join(sorted(self.VALID_ROLES))
            raise ValueError(f"Role '{role}' is not valid. Use: {valid}")
        model = UserModel(name=name, email=email, role=role)
        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return _map_user(model)
        except IntegrityError as error:
            self.db.rollback()
            raise ValueError(
                f"Email '{email}' is already registered in the system."
            ) from error

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if row is None:
            raise ValueError(f"User with id {user_id} does not exist")
        return _map_user(row)


class TimeBlockRepositorySQL(ITimeBlockRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_available_blocks(self, room_id: int) -> List[TimeBlock]:
        booked_blocks = select(AssignmentModel.time_block_id).where(
            AssignmentModel.room_id == room_id,
            AssignmentModel.status == "CONFIRMADA",
        )
        rows = (
            self.db.query(TimeBlockModel)
            .filter(TimeBlockModel.id.notin_(booked_blocks))
            .order_by(TimeBlockModel.weekday, TimeBlockModel.start_time)
            .all()
        )
        return [_map_time_block(row) for row in rows]

    def get_all_blocks(self) -> List[TimeBlock]:
        rows = (
            self.db.query(TimeBlockModel)
            .order_by(TimeBlockModel.weekday, TimeBlockModel.start_time)
            .all()
        )
        return [_map_time_block(row) for row in rows]
