# backend/main.py

import sys
import os
from typing import List as TypingList

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import schemas

from infrastructure.crear_db import SessionLocal, Asignacion as AsignacionDB
from infrastructure.repository import (
    SalaRepositorySQL,
    AsignacionRepositorySQL,
    BloqueHorarioRepositorySQL,
)
from use_cases.asignar_sala import AsignacionUseCase

app = FastAPI(title="API Asignación de Salas - Comando Estelar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# ENDPOINTS EXISTENTES
# ==========================================

@app.post("/api/sugerir-salas", response_model=schemas.SugerenciaResponse)
def sugerir_salas(solicitud: schemas.SolicitudSugerencia, db: Session = Depends(get_db)):
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    bloque_repo = BloqueHorarioRepositorySQL(db)

    use_case = AsignacionUseCase(sala_repo, asignacion_repo, bloque_repo)
    salas_optimas = use_case.sugerir_salas_optimas(
        bloque_id=solicitud.bloque_id,
        aforo_esperado=solicitud.aforo_esperado,
        necesita_proyector=solicitud.necesita_proyector,
        necesita_enchufes=solicitud.necesita_enchufes,
    )

    if not salas_optimas:
        return {"mensaje": "No se encontraron salas que cumplan los requisitos.", "salas_sugeridas": []}
    return {"mensaje": "Salas encontradas con éxito.", "salas_sugeridas": salas_optimas}


@app.post("/api/asignar", response_model=schemas.AsignacionResponse)
def confirmar_asignacion(confirmacion: schemas.ConfirmacionAsignacion, db: Session = Depends(get_db)):
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    bloque_repo = BloqueHorarioRepositorySQL(db)

    use_case = AsignacionUseCase(sala_repo, asignacion_repo, bloque_repo)
    try:
        asignacion = use_case.confirmar_asignacion(
            seccion_id=confirmacion.seccion_id,
            sala_id=confirmacion.sala_id,
            bloque_id=confirmacion.bloque_id,
            coordinador_id=confirmacion.coordinador_id,
        )
        return asignacion
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# NUEVOS ENDPOINTS GET
# ==========================================

@app.get("/api/estadisticas")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Devuelve conteos reales de salas por estado para los dashboards.
    """
    sala_repo = SalaRepositorySQL(db)
    todas = sala_repo.obtener_todas_las_salas()

    total = len(todas)
    asignadas = sum(1 for s in todas if s.estado == "ASIGNADA")
    mantenimiento = sum(1 for s in todas if s.estado == "MANTENIMIENTO")
    disponibles = sum(1 for s in todas if s.estado == "DISPONIBLE")
    ocupacion = round((asignadas / total) * 100) if total > 0 else 0

    asignacion_repo = AsignacionRepositorySQL(db)
    total_asignaciones = len(asignacion_repo.obtener_todas_las_asignaciones())

    return {
        "total_salas": total,
        "disponibles": disponibles,
        "asignadas": asignadas,
        "mantenimiento": mantenimiento,
        "ocupacion_pct": ocupacion,
        "total_asignaciones": total_asignaciones,
    }


@app.get("/api/salas", response_model=TypingList[schemas.SalaResponse])
def listar_todas_las_salas(db: Session = Depends(get_db)):
    """
    Retorna el inventario completo de salas (para el panel de mapa/inventario).
    """
    sala_repo = SalaRepositorySQL(db)
    return sala_repo.obtener_todas_las_salas()


@app.get("/api/asignaciones-detalle")
def listar_asignaciones_detalle(db: Session = Depends(get_db)):
    """
    Retorna asignaciones confirmadas con datos enriquecidos (sala, bloque).
    Se usa en la vista 'Mis Solicitudes' del profesor.
    """
    asignaciones = (
        db.query(AsignacionDB)
        .filter(AsignacionDB.estado == "CONFIRMADA")
        .order_by(AsignacionDB.creado_en.desc())
        .all()
    )

    result = []
    for a in asignaciones:
        result.append({
            "id": a.id,
            "seccion_id": a.seccion_id,
            "sala_codigo": a.sala.codigo if a.sala else f"#{a.sala_id}",
            "sala_capacidad": a.sala.capacidad if a.sala else 0,
            "bloque_dia": a.bloque.dia_semana if a.bloque else "—",
            "bloque_inicio": str(a.bloque.hora_inicio)[:5] if a.bloque else "—",
            "bloque_fin": str(a.bloque.hora_fin)[:5] if a.bloque else "—",
            "estado": a.estado,
            "creado_en": a.creado_en.strftime("%d/%m/%Y %H:%M") if a.creado_en else "—",
        })
    return result
