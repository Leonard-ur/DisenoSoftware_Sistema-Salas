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
    is_accessible: bool   # BR-08
    tags: Optional[str]   # BR-09


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