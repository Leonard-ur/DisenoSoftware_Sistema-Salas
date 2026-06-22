# domain/ports.py

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities import Assignment, Room, TimeBlock, User


class IRoomRepository(ABC):
    """Output port to interact with the room inventory."""

    @abstractmethod
    def get_all_rooms(self) -> List[Room]:
        ...

    @abstractmethod
    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        ...

    @abstractmethod
    def get_available_rooms(self) -> List[Room]:
        ...

    @abstractmethod
    def search_rooms(
        self,
        attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
    ) -> List[Room]:
        ...


class IAssignmentRepository(ABC):
    """Output port to manage assignments."""

    @abstractmethod
    def save_request(
        self,
        section_id: int,
        room_id: int,
        time_block_id: int,
        confirmed_by: int,
    ) -> Assignment:
        ...

    @abstractmethod
    def get_all_assignments(self) -> List[Assignment]:
        ...

    @abstractmethod
    def get_detailed_assignments(self) -> List[dict]:
        """Return a read model (DTO) with cross-referenced data for the view."""
        ...


class IUserRepository(ABC):
    """Output port to manage users."""

    @abstractmethod
    def add_user(self, name: str, email: str, role: str) -> User:
        ...

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        ...


class ITimeBlockRepository(ABC):
    """Output port to manage time blocks."""

    @abstractmethod
    def get_available_blocks(self, room_id: int) -> List[TimeBlock]:
        ...

    @abstractmethod
    def get_all_blocks(self) -> List[TimeBlock]:
        ...
