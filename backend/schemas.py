from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ==========================================
# AUTH
# ==========================================


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str
    name: str
    user_id: int


# ==========================================
# ROOM REQUESTS (solicitudes de docentes)
# ==========================================


class RoomRequestSchema(BaseModel):
    """A pending room request made by a teacher."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    teacher_name: str
    course_name: str
    expected_attendance: int
    requires_projector: bool
    requires_outlets: bool
    requires_accessibility: bool
    time_block_id: Optional[int]
    time_block_day: Optional[str]
    time_block_start: Optional[str]
    time_block_end: Optional[str]
    status: str


class RoomSuggestionRequest(BaseModel):
    """Requirements sent by the user to search for a room."""

    time_block_id: int
    expected_attendance: int
    requires_projector: bool
    requires_outlets: bool


class AssignmentRequest(BaseModel):
    """Data needed to confirm an assignment."""

    section_id: int
    room_id: int
    time_block_id: int
    coordinator_id: int


class RoomResponse(BaseModel):
    """Basic representation of a room."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    capacity: int
    status: str
    has_projector: bool
    usable_outlets: int


class RoomSuggestionResponse(BaseModel):
    """Response holding the list of recommended rooms."""

    message: str
    suggested_rooms: List[RoomResponse]


class AssignmentResponse(BaseModel):
    """Basic confirmation of a created assignment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    section_id: int
    room_id: int
    time_block_id: int
    status: str


class AssignmentDetailResponse(BaseModel):
    """Detailed assignment information for the end user."""

    id: int
    section_id: int
    room_code: str
    room_capacity: int
    time_block_day: str
    time_block_start: str
    time_block_end: str
    status: str
    created_at: str


class TimeBlockResponse(BaseModel):
    """Representation of a time block."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    weekday: str
    start_time: str
    end_time: str
