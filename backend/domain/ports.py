# domain/ports.py

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Sala, Usuario, Asignacion, BloqueHorario

class ISalaRepository(ABC):
    """Puerto de salida para interactuar con el inventario de Salas"""
    
    @abstractmethod
    def obtener_todas_las_salas(self) -> List[Sala]:
        pass

    @abstractmethod
    def obtener_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        pass

    @abstractmethod
    def obtener_salas_disponibles(self) -> List[Sala]:
        pass

    @abstractmethod
    def buscar_salas(self, aforo: int, necesita_proyector: bool, necesita_enchufes: bool) -> List[Sala]:
        pass


class IAsignacionRepository(ABC):
    """Puerto de salida para gestionar las asignaciones"""
    
    @abstractmethod
    def guardar_solicitud(self, seccion_id: int, sala_id: int, bloque_id: int, confirmado_por: int) -> Asignacion:
        pass

    @abstractmethod
    def obtener_todas_las_asignaciones(self) -> List[Asignacion]:
        pass

    @abstractmethod
    def obtener_asignaciones_detalladas(self) -> List[dict]:
        """Retorna un Read Model (DTO) con los datos cruzados para la vista del usuario"""
        pass


class IUsuarioRepository(ABC):
    """Puerto de salida para gestionar usuarios"""
    
    @abstractmethod
    def añadir_usuario(self, nombre: str, email: str, rol: str) -> Usuario:
        pass

    @abstractmethod
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass


class IBloqueHorarioRepository(ABC):
    """Puerto de salida para gestionar los bloques horarios"""
    
    @abstractmethod
    def obtener_bloque_disponible(self, sala_id: int) -> List[BloqueHorario]:
        pass

    @abstractmethod
    def obtener_todos_los_bloques(self) -> List[BloqueHorario]:
        pass