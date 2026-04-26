"""
Caso de uso principal: AsignarSala.

Orquesta las reglas de negocio para encontrar y reservar la sala más
adecuada para una solicitud dada, sin depender de ninguna tecnología
concreta (Clean Architecture – Use Cases Layer).

Reglas de negocio aplicadas:
    1. Aforo:        capacidad_sala >= alumnos_inscritos
    2. Disponibilidad: sin traslapes de horario con otras reservas
    3. Equipamiento:  la sala debe tener *todos* los recursos requeridos
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.domain.models import Asignacion, Sala, SolicitudAsignacion
from backend.domain.ports import LockService, SalaRepository


# ---------------------------------------------------------------------------
# Excepciones de dominio
# ---------------------------------------------------------------------------

class SalaNoDisponibleError(Exception):
    """Se lanza cuando ninguna sala cumple todos los criterios."""


# ---------------------------------------------------------------------------
# Caso de Uso
# ---------------------------------------------------------------------------

@dataclass
class AsignarSala:
    """
    Caso de uso que selecciona y asigna la sala óptima para una solicitud.

    Dependencias inyectadas a través de los puertos del dominio:
        sala_repo:    Repositorio de salas (lectura y consulta de reservas).
        lock_service: Servicio de bloqueo temporal para evitar doble reserva.
    """

    sala_repo: SalaRepository
    lock_service: LockService

    def ejecutar(self, solicitud: SolicitudAsignacion) -> Asignacion:
        """
        Encuentra y reserva la sala más adecuada para la solicitud.

        Algoritmo:
            1. Obtiene las salas ya reservadas en el rango horario.
            2. Filtra las salas libres por aforo y equipamiento.
            3. De las candidatas, elige la de menor capacidad que aún
               cubra los alumnos inscritos (uso eficiente del espacio).
            4. Adquiere un bloqueo temporal sobre la sala elegida.
            5. Registra la reserva (delega en el repositorio).
            6. Libera el bloqueo y retorna la asignación.

        Args:
            solicitud: Datos de la solicitud a procesar.

        Returns:
            Objeto Asignacion con la sala seleccionada y la solicitud original.

        Raises:
            SalaNoDisponibleError: Si ninguna sala cumple los criterios.
        """
        # --- 1. Salas ya ocupadas en ese rango horario --------------------
        ids_ocupadas = set(
            self.sala_repo.salas_reservadas_en_rango(
                solicitud.inicio, solicitud.fin
            )
        )

        # --- 2. Filtrado por disponibilidad, aforo y equipamiento ---------
        candidatas = [
            sala
            for sala in self.sala_repo.listar_todas()
            if self._esta_disponible(sala, ids_ocupadas)
            and self._cumple_aforo(sala, solicitud)
            and self._cumple_equipamiento(sala, solicitud)
        ]

        if not candidatas:
            raise SalaNoDisponibleError(
                f"No hay salas disponibles para la solicitud '{solicitud.id}' "
                f"({solicitud.alumnos_inscritos} alumnos, "
                f"equipamiento: {solicitud.equipamiento_requerido})."
            )

        # --- 3. Selección: menor capacidad suficiente ---------------------
        sala_elegida: Sala = min(candidatas, key=lambda s: s.capacidad)

        # --- 4. Bloqueo temporal para evitar reservas concurrentes --------
        if not self.lock_service.adquirir(sala_elegida.id):
            raise SalaNoDisponibleError(
                f"La sala '{sala_elegida.id}' está siendo reservada "
                "por otro proceso. Intente nuevamente."
            )

        try:
            # --- 5. Registrar reserva en el repositorio -------------------
            self.sala_repo.registrar_reserva(sala_elegida.id, solicitud)
        finally:
            # --- 6. Liberar bloqueo siempre, incluso ante errores ---------
            self.lock_service.liberar(sala_elegida.id)

        return Asignacion(sala=sala_elegida, solicitud=solicitud)

    # ------------------------------------------------------------------
    # Métodos privados de validación (reglas de negocio)
    # ------------------------------------------------------------------

    @staticmethod
    def _esta_disponible(sala: Sala, ids_ocupadas: set) -> bool:
        """Regla: la sala no debe estar reservada en el horario solicitado."""
        return sala.id not in ids_ocupadas

    @staticmethod
    def _cumple_aforo(sala: Sala, solicitud: SolicitudAsignacion) -> bool:
        """Regla: capacidad_sala >= alumnos_inscritos."""
        return sala.capacidad >= solicitud.alumnos_inscritos

    @staticmethod
    def _cumple_equipamiento(
        sala: Sala, solicitud: SolicitudAsignacion
    ) -> bool:
        """Regla: la sala debe poseer TODOS los recursos requeridos."""
        requeridos = set(solicitud.equipamiento_requerido)
        disponibles = set(sala.equipamiento)
        return requeridos.issubset(disponibles)
