# backend/main.py

import sys
import os
from typing import List as TypingList

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import schemas

from infrastructure.crear_db import SessionLocal
from infrastructure.repository import (
    SalaRepositorySQL,
    AsignacionRepositorySQL,
    BloqueHorarioRepositorySQL,
)
from use_cases.asignar_sala import AsignacionUseCase
from use_cases.dashboard import DashboardUseCase

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
# ENDPOINTS DE ASIGNACIÓN
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
# ENDPOINTS DE DASHBOARD Y LISTADOS
# ==========================================

@app.get("/api/estadisticas")
def obtener_estadisticas(db: Session = Depends(get_db)):
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    
    use_case = DashboardUseCase(sala_repo, asignacion_repo)
    return use_case.obtener_estadisticas_generales()


@app.get("/api/salas", response_model=TypingList[schemas.SalaResponse])
def listar_todas_las_salas(db: Session = Depends(get_db)):
    sala_repo = SalaRepositorySQL(db)
    return sala_repo.obtener_todas_las_salas()


@app.get("/api/asignaciones-detalle")
def listar_asignaciones_detalle(db: Session = Depends(get_db)):
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    
    use_case = DashboardUseCase(sala_repo, asignacion_repo)
    return use_case.listar_asignaciones_profesor()