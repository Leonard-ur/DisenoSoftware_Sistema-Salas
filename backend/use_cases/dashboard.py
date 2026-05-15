# use_cases/dashboard.py

from domain.ports import ISalaRepository, IAsignacionRepository

class DashboardUseCase:
    def __init__(self, sala_repo: ISalaRepository, asignacion_repo: IAsignacionRepository):
        self.sala_repo = sala_repo
        self.asignacion_repo = asignacion_repo

    def obtener_estadisticas_generales(self) -> dict:
        """
        Calcula las estadísticas para el panel de control.
        """
        todas = self.sala_repo.obtener_todas_las_salas()
        
        total = len(todas)
        asignadas = sum(1 for s in todas if s.estado == "ASIGNADA")
        mantenimiento = sum(1 for s in todas if s.estado == "MANTENIMIENTO")
        disponibles = sum(1 for s in todas if s.estado == "DISPONIBLE")
        ocupacion = round((asignadas / total) * 100) if total > 0 else 0

        total_asignaciones = len(self.asignacion_repo.obtener_todas_las_asignaciones())

        return {
            "total_salas": total,
            "disponibles": disponibles,
            "asignadas": asignadas,
            "mantenimiento": mantenimiento,
            "ocupacion_pct": ocupacion,
            "total_asignaciones": total_asignaciones,
        }

    def listar_asignaciones_profesor(self) -> list:
        """
        Retorna la lista detallada de asignaciones.
        """
        return self.asignacion_repo.obtener_asignaciones_detalladas()