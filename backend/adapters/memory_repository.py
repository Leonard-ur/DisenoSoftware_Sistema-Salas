"""
Adaptadores en memoria (mock) para el Sistema de Asignación de Salas.

Implementan los puertos del dominio usando estructuras de datos Python puras
(listas y diccionarios), lo que permite ejecutar y probar toda la lógica de
negocio sin necesidad de instalar una base de datos real ni ningún framework
externo (Clean Architecture – Adapters Layer).
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from backend.domain.models import Sala, SolicitudAsignacion
from backend.domain.ports import LockService, SalaRepository


class MemorySalaRepository(SalaRepository):
    """
    Implementación en memoria del repositorio de salas.

    Los datos se inicializan con un catálogo de muestra que representa
    aulas reales de una institución universitaria típica.  El catálogo
    y las reservas se almacenan en listas/diccionarios de Python; no se
    persiste nada entre reinicios del proceso.

    Estructura interna:
        _salas:    Dict[sala_id, Sala]
        _reservas: List[(sala_id, inicio, fin, solicitud_id)]
    """

    # Catálogo de salas de muestra
    _CATALOGO_INICIAL: List[Dict] = [
        {
            "id": "S-101",
            "nombre": "Aula Magna 101",
            "capacidad": 120,
            "equipamiento": ["proyector", "aire_acondicionado", "microfono"],
        },
        {
            "id": "S-102",
            "nombre": "Laboratorio Informática 102",
            "capacidad": 40,
            "equipamiento": ["proyector", "computadoras", "aire_acondicionado"],
        },
        {
            "id": "S-103",
            "nombre": "Aula Estándar 103",
            "capacidad": 60,
            "equipamiento": ["proyector", "aire_acondicionado"],
        },
        {
            "id": "S-104",
            "nombre": "Sala de Seminarios 104",
            "capacidad": 25,
            "equipamiento": ["proyector", "videoconferencia"],
        },
        {
            "id": "S-105",
            "nombre": "Aula Básica 105",
            "capacidad": 35,
            "equipamiento": [],
        },
    ]

    def __init__(self) -> None:
        # Construir el diccionario de salas desde el catálogo inicial
        self._salas: Dict[str, Sala] = {
            d["id"]: Sala(
                id=d["id"],
                nombre=d["nombre"],
                capacidad=d["capacidad"],
                equipamiento=d["equipamiento"],
            )
            for d in self._CATALOGO_INICIAL
        }

        # Lista de tuplas (sala_id, inicio, fin, solicitud_id)
        self._reservas: List[Tuple[str, datetime, datetime, str]] = []

    # ------------------------------------------------------------------
    # Implementación de SalaRepository
    # ------------------------------------------------------------------

    def listar_todas(self) -> List[Sala]:
        """Devuelve todas las salas del catálogo."""
        return list(self._salas.values())

    def buscar_por_id(self, sala_id: str) -> Optional[Sala]:
        """Devuelve la sala con el id dado, o None si no existe."""
        return self._salas.get(sala_id)

    def salas_reservadas_en_rango(
        self, inicio: datetime, fin: datetime
    ) -> List[str]:
        """
        Devuelve los ids de salas con reservas que se solapan con [inicio, fin).

        Dos intervalos [a, b) y [c, d) se solapan si a < d y c < b.
        """
        ocupadas: List[str] = []
        for sala_id, res_inicio, res_fin, _ in self._reservas:
            if inicio < res_fin and res_inicio < fin:
                ocupadas.append(sala_id)
        return ocupadas

    def registrar_reserva(
        self, sala_id: str, solicitud: SolicitudAsignacion
    ) -> None:
        """
        Registra una reserva para la sala indicada.

        Args:
            sala_id:   Id de la sala a reservar.
            solicitud: Solicitud que origina la reserva.

        Raises:
            ValueError: Si la sala no existe en el catálogo.
        """
        if sala_id not in self._salas:
            raise ValueError(f"Sala '{sala_id}' no encontrada en el catálogo.")
        self._reservas.append(
            (sala_id, solicitud.inicio, solicitud.fin, solicitud.id)
        )

    def listar_reservas(self) -> List[Dict]:
        """
        Devuelve todas las reservas registradas (útil para depuración).

        Returns:
            Lista de diccionarios con sala_id, inicio, fin y solicitud_id.
        """
        return [
            {
                "sala_id": sala_id,
                "inicio": inicio.isoformat(),
                "fin": fin.isoformat(),
                "solicitud_id": sol_id,
            }
            for sala_id, inicio, fin, sol_id in self._reservas
        ]


class MemoryLockService(LockService):
    """
    Implementación en memoria del servicio de bloqueos.

    Usa un conjunto protegido por un ``threading.Lock`` de Python para
    registrar qué salas están bloqueadas en este momento.  Es seguro para
    uso multihilo dentro de un mismo proceso, aunque no escala a múltiples
    instancias (para eso se usaría Redis u otro backend distribuido).
    """

    def __init__(self) -> None:
        self._bloqueadas: set = set()
        self._mutex = threading.Lock()

    def adquirir(self, sala_id: str, duracion_segundos: int = 30) -> bool:
        """
        Intenta bloquear la sala.  Devuelve False si ya está bloqueada.

        Note:
            La duración del bloqueo (duracion_segundos) se ignora en esta
            implementación en memoria; se mantiene el parámetro para respetar
            el contrato del puerto.
        """
        with self._mutex:
            if sala_id in self._bloqueadas:
                return False
            self._bloqueadas.add(sala_id)
            return True

    def liberar(self, sala_id: str) -> None:
        """Libera el bloqueo sobre la sala."""
        with self._mutex:
            self._bloqueadas.discard(sala_id)
