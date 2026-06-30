from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RoomSuggestionRequest(BaseModel):
    """Requirements sent by the user to search for a room."""

    time_block_id: int
    expected_attendance: int
    requires_projector: bool
    requires_outlets: bool
    requires_accessibility: bool = False   # BR-08
    required_tags: Optional[str] = None    # BR-09


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str
    name: str
    user_id: int


# ==========================================
# ROOMS
# ==========================================


class RoomResponse(BaseModel):
    """Full representation of a room."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    capacity: int
    status: str
    has_projector: bool
    usable_outlets: int
    is_accessible: bool
    tags: Optional[str]


# ==========================================
# ROOM REQUESTS (solicitudes de docentes)
# ==========================================


class RoomRequestCreate(BaseModel):
    """Payload that a teacher sends to create a room request."""

    teacher_id: int
    course_name: str
    expected_attendance: int
    requires_projector: bool = False
    requires_outlets: bool = False
    requires_accessibility: bool = False
    time_block_id: Optional[int] = None


class RoomRequestStatusUpdate(BaseModel):
    """Payload that a coordinator sends to approve or reject a request."""

    status: str   # APROBADA | RECHAZADA


class RoomRequestResponse(BaseModel):
    """Full detail of a room request, including teacher and block info."""

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
    created_at: Optional[str]


# kept for backwards compatibility with existing frontend
RoomRequestSchema = RoomRequestResponse


# ==========================================
# ROOM SUGGESTIONS (motor de búsqueda)
# ==========================================


class RoomSuggestionResponse(BaseModel):
    """Response holding the list of recommended rooms."""

    message: str
    suggested_rooms: List[RoomResponse]


# ==========================================
# ASSIGNMENTS
# ==========================================


class AssignmentRequest(BaseModel):
    """Data needed to confirm an assignment."""

    section_id: int
    room_id: int
    time_block_id: int
    coordinator_id: int


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


# ==========================================
# TIME BLOCKS
# ==========================================


class TimeBlockResponse(BaseModel):
    """Representation of a time block."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    weekday: str
    start_time: str
    end_time: str
