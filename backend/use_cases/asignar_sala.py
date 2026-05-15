# use_cases/asignar_sala.py

from typing import List
from domain.entities import Sala, Asignacion
from domain.ports import ISalaRepository, IAsignacionRepository, IBloqueHorarioRepository

class AsignacionUseCase:
    def __init__(
        self, 
        sala_repo: ISalaRepository, 
        asignacion_repo: IAsignacionRepository,
        bloque_repo: IBloqueHorarioRepository
    ):
        """
        Inyección de Dependencias: El caso de uso no crea las conexiones a la BD.
        Las recibe desde afuera (pasadas por el Arquitecto desde main.py).
        """
        self.sala_repo = sala_repo
        self.asignacion_repo = asignacion_repo
        self.bloque_repo = bloque_repo

    def sugerir_salas_optimas(
        self, 
        bloque_id: int, 
        aforo_esperado: int, 
        necesita_proyector: bool, 
        necesita_enchufes: bool
    ) -> List[Sala]:
        """
        FR-04 (Sugerencia Óptima): Evalúa y retorna las mejores salas ordenadas por eficiencia.
        """
        # 1. Obtener todas las salas que físicamente están operativas
        salas_disponibles = self.sala_repo.obtener_salas_disponibles()
        
        salas_candidatas = []
        
        for sala in salas_disponibles:
            # 2. Aplicar reglas de negocio inmutables (BR-01 Aforo, BR-03 Equipamiento)
            # Delegamos la validación a la propia Entidad 'Sala'
            if not sala.cumple_requisitos(aforo_esperado, necesita_proyector, necesita_enchufes):
                continue
                
            # 3. Validar disponibilidad temporal (BR-02 Traslapes)
            # Pedimos al puerto los bloques donde esta sala NO está ocupada
            bloques_libres = self.bloque_repo.obtener_bloque_disponible(sala.id)
            bloques_libres_ids = [b.id for b in bloques_libres]
            
            if bloque_id not in bloques_libres_ids:
                continue # Hay traslape, la sala está ocupada en este bloque horario
                
            salas_candidatas.append(sala)
            
        # 4. Calcular Score de Eficiencia (FR-04)
        # Delegamos el cálculo matemático a la Entidad (Information Expert Pattern).
        # Ordenamos de menor a mayor score (menor score = menos asientos sobrantes = más eficiente).
        salas_ordenadas = sorted(
            salas_candidatas, 
            key=lambda s: s.calcular_score_eficiencia(aforo_esperado)
        )
        
        return salas_ordenadas

    def confirmar_asignacion(
        self, 
        seccion_id: int, 
        sala_id: int, 
        bloque_id: int, 
        coordinador_id: int
    ) -> Asignacion:
        """
        FR-06 (Confirmación): Registra la asignación final.
        BR-05 (Concurrencia): Si dos coordinadores intentan asignar la misma sala al mismo tiempo,
        el puerto (repositorio) lanzará un ValueError que atajaremos aquí.
        """
        try:
            asignacion = self.asignacion_repo.guardar_solicitud(
                seccion_id=seccion_id,
                sala_id=sala_id,
                bloque_id=bloque_id,
                confirmado_por=coordinador_id
            )
            return asignacion
        except ValueError as e:
            # Capturamos el error de concurrencia/integridad y lo subimos a la capa Web
            raise Exception(f"Conflicto al asignar: {str(e)}")