# domain/entities.py

import math
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class Room:
    id: Optional[int]
    code: str
    capacity: int
    status: str
    has_projector: bool
    usable_outlets: int
    is_accessible: bool = False
    tags: Optional[str] = None

    def is_available(self) -> bool:
        """Return True when the room is neither under maintenance nor assigned."""
        return self.status == "DISPONIBLE"

    def effective_capacity(self) -> int:
        """
        BR-01 (Legal and sanitary capacity):
        The real allowed capacity is 95% of the physical capacity.
        math.floor rounds down for safety
        (e.g. 41 * 0.95 = 38.95 -> 38 real seats).
        """
        return math.floor(self.capacity * 0.95)

    def meets_requirements(
        self,
        expected_attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
    ) -> bool:
        """
        Apply the business rules:
        - BR-01 (Capacity): effective capacity >= expected attendance.
        - BR-03 (Equipment): validate projector and outlets when required.
        """
        if self.effective_capacity() < expected_attendance:
            return False
        if requires_projector and not self.has_projector:
            return False
        if requires_outlets and self.usable_outlets <= 0:
            return False
        return True

    def efficiency_score(self, expected_attendance: int) -> int:
        """
        FR-04 (Optimal suggestion): compute the leftover seats.
        A lower score means higher efficiency (less wasted space).
        """
        return self.effective_capacity() - expected_attendance


@dataclass
class RoomRequest:
    id: Optional[int]
    teacher_id: int
    course_name: str
    expected_attendance: int
    requires_projector: bool
    requires_outlets: bool
    requires_accessibility: bool
    time_block_id: Optional[int]
    # PENDIENTE | APROBADA | RECHAZADA
    status: str = "PENDIENTE"
    created_at: Optional[datetime] = None


@dataclass
class Section:
    id: Optional[int]
    code: str
    enrolled_count: int
    requires_projector: bool
    requires_outlets: bool
    teacher_id: int


@dataclass
class TimeBlock:
    id: Optional[int]
    weekday: str
    start_time: time
    end_time: time


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    role: str


@dataclass
class Assignment:
    id: Optional[int]
    section_id: int
    room_id: int
    time_block_id: int
    status: str
    confirmed_by: int
    created_at: Optional[datetime] = None
