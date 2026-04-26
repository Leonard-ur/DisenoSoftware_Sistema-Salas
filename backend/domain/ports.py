"""
Puertos (interfaces) del dominio para el Sistema de Asignación de Salas.

Define los contratos que deben cumplir los adaptadores externos sin
importar la tecnología concreta que los implemente (Clean Architecture –
Ports & Adapters).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from backend.domain.models import Sala, SolicitudAsignacion


class SalaRepository(ABC):
    """
    Puerto de acceso a la colección de salas.

    Los adaptadores concretos (base de datos, memoria, archivo, etc.)
    deben implementar esta interfaz para que el dominio permanezca
    desacoplado de la tecnología de persistencia.
    """

    @abstractmethod
    def listar_todas(self) -> List[Sala]:
        """Devuelve todas las salas disponibles en el sistema."""
        ...

    @abstractmethod
    def buscar_por_id(self, sala_id: str) -> Optional[Sala]:
        """
        Devuelve la sala con el id indicado, o None si no existe.

        Args:
            sala_id: Identificador único de la sala.
        """
        ...

    @abstractmethod
    def salas_reservadas_en_rango(
        self, inicio: datetime, fin: datetime
    ) -> List[str]:
        """
        Devuelve los ids de salas que tienen al menos una reserva
        que se traslapa con el rango [inicio, fin).

        Args:
            inicio: Inicio del intervalo de búsqueda.
            fin:    Fin del intervalo de búsqueda.
        """
        ...

    @abstractmethod
    def registrar_reserva(
        self,
        sala_id: str,
        solicitud: SolicitudAsignacion,
    ) -> None:
        """
        Persiste la reserva de la sala para la solicitud dada.

        Args:
            sala_id:   Id de la sala a reservar.
            solicitud: Solicitud que origina la reserva.
        """
        ...


class LockService(ABC):
    """
    Puerto para bloquear una sala temporalmente mientras se completa
    el proceso de asignación, previniendo condiciones de carrera.

    En producción podría implementarse con Redis, un semáforo de base
    de datos, etc. En entornos de prueba basta con un mock en memoria.
    """

    @abstractmethod
    def adquirir(self, sala_id: str, duracion_segundos: int = 30) -> bool:
        """
        Intenta adquirir un bloqueo exclusivo sobre la sala.

        Args:
            sala_id:           Id de la sala a bloquear.
            duracion_segundos: Tiempo máximo que durará el bloqueo.

        Returns:
            True si el bloqueo fue adquirido, False si ya estaba tomado.
        """
        ...

    @abstractmethod
    def liberar(self, sala_id: str) -> None:
        """
        Libera el bloqueo sobre la sala.

        Args:
            sala_id: Id de la sala cuyo bloqueo se libera.
        """
        ...
