# use_cases/assignment.py

from typing import List

from domain.entities import Assignment, Room
from domain.ports import (
    IAssignmentRepository,
    IRoomRepository,
    ITimeBlockRepository,
)


class AssignmentUseCase:
    def __init__(
        self,
        room_repo: IRoomRepository,
        assignment_repo: IAssignmentRepository,
        time_block_repo: ITimeBlockRepository,
    ):
        """
        Dependency injection: the use case does not create the database
        connections. They are provided from the outside (wired in main.py).
        """
        self.room_repo = room_repo
        self.assignment_repo = assignment_repo
        self.time_block_repo = time_block_repo

    def suggest_optimal_rooms(
        self,
        time_block_id: int,
        expected_attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
        requires_accessibility: bool = False,   # BR-08
        required_tags: str | None = None,       # BR-09
    ) -> List[Room]:
        """
        FR-04 (Optimal suggestion): evaluate the operational rooms and return
        the eligible ones sorted by efficiency (least wasted space first).
        Filters by capacity, equipment, accessibility, tag and time block.
        """
        candidates = [
            room
            for room in self.room_repo.get_available_rooms()
            if self._is_eligible(
                room,
                time_block_id,
                expected_attendance,
                requires_projector,
                requires_outlets,
                requires_accessibility,
                required_tags,
            )
        ]
        return sorted(
            candidates,
            key=lambda room: room.efficiency_score(expected_attendance),
        )

    def _is_eligible(
        self,
        room: Room,
        time_block_id: int,
        expected_attendance: int,
        requires_projector: bool,
        requires_outlets: bool,
        requires_accessibility: bool = False,   # BR-08
        required_tags: str | None = None,       # BR-09
    ) -> bool:
        """
        Check the immutable business rules for a single room:
        - BR-01 (Capacity), BR-03 (Equipment), BR-08 (Accessibility),
          BR-09 (Lab affinity) — all delegated to the entity.
        - BR-02 (Overlap): the room must be free in the requested time block.
        - Accessibility and tag filters when requested.
        """
        if not room.meets_requirements(
            expected_attendance,
            requires_projector,
            requires_outlets,
            requires_accessibility=requires_accessibility,
            required_tags=required_tags,
        ):
            return False
        if requires_accessibility and not room.is_accessible:
            return False
        free_block_ids = {
            block.id
            for block in self.time_block_repo.get_available_blocks(room.id)
        }
        return time_block_id in free_block_ids

    def confirm_assignment(
        self,
        section_id: int,
        room_id: int,
        time_block_id: int,
        coordinator_id: int,
    ) -> Assignment:
        """
        FR-06 (Confirmation): register the final assignment.
        BR-05 (Concurrency): if two coordinators try to book the same room at
        the same time, the repository raises ValueError, re-raised here as a
        RuntimeError for the web layer to translate into an HTTP error.
        """
        try:
            return self.assignment_repo.save_request(
                section_id=section_id,
                room_id=room_id,
                time_block_id=time_block_id,
                confirmed_by=coordinator_id,
            )
        except ValueError as error:
            raise RuntimeError(f"Assignment conflict: {error}") from error
