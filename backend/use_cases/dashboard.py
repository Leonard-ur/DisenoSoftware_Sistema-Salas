# use_cases/dashboard.py

from typing import List

from domain.entities import Room
from domain.ports import IAssignmentRepository, IRoomRepository


class DashboardUseCase:
    def __init__(
        self,
        room_repo: IRoomRepository,
        assignment_repo: IAssignmentRepository,
    ):
        self.room_repo = room_repo
        self.assignment_repo = assignment_repo

    def get_general_statistics(self) -> dict:
        """Compute the statistics shown in the control panel."""
        rooms = self.room_repo.get_all_rooms()
        total = len(rooms)
        assigned = self._count_by_status(rooms, "ASIGNADA")
        maintenance = self._count_by_status(rooms, "MANTENIMIENTO")
        available = self._count_by_status(rooms, "DISPONIBLE")
        occupancy = round((assigned / total) * 100) if total > 0 else 0
        total_assignments = len(self.assignment_repo.get_all_assignments())
        return {
            "total_rooms": total,
            "available": available,
            "assigned": assigned,
            "maintenance": maintenance,
            "occupancy_pct": occupancy,
            "total_assignments": total_assignments,
        }

    @staticmethod
    def _count_by_status(rooms: List[Room], status: str) -> int:
        return sum(1 for room in rooms if room.status == status)

    def list_teacher_assignments(self) -> List[dict]:
        """Return the detailed list of assignments for the end user."""
        return self.assignment_repo.get_detailed_assignments()
