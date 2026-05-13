# backend/main.py

import sys
import os

# ==========================================
# FIX DE RUTAS (Evita errores de importación)
# ==========================================
# Esto le dice a Python que la carpeta "backend" es la raíz del proyecto.
# Así, cuando digamos "from infrastructure...", Python sabrá dónde buscar.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importar esquemas (Tu trabajo)
import schemas

# Importar Base de Datos y Repositorios (El trabajo de Lucas)
from infrastructure.crear_db import SessionLocal
from infrastructure.repository import SalaRepositorySQL, AsignacionRepositorySQL, BloqueHorarioRepositorySQL

# Importar Casos de Uso (El trabajo de Camilo)
from use_cases.asignar_sala import AsignacionUseCase

# Inicializamos la aplicación FastAPI
app = FastAPI(title="API Asignación de Salas - Comando Estelar")

# ==========================================
# CONFIGURACIÓN CORS (Para que el Frontend pueda conectarse)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que cualquier página web consulte esta API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# DEPENDENCIA DE BASE DE DATOS
# ==========================================
def get_db():
    """
    Abre una sesión con la base de datos para cada petición web
    y la cierra automáticamente al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# ENDPOINTS (Rutas Web)
# ==========================================

@app.post("/api/sugerir-salas", response_model=schemas.SugerenciaResponse)
def sugerir_salas(solicitud: schemas.SolicitudSugerencia, db: Session = Depends(get_db)):
    """
    Recibe los datos del Frontend, ensambla las piezas y ejecuta el Motor de Reglas.
    """
    # 1. Instanciar los repositorios de Lucas pasándoles la conexión a la BD
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    bloque_repo = BloqueHorarioRepositorySQL(db)

    # 2. Instanciar el Caso de Uso de Camilo inyectando los repositorios
    use_case = AsignacionUseCase(sala_repo, asignacion_repo, bloque_repo)

    # 3. Ejecutar la lógica de negocio pura
    salas_optimas = use_case.sugerir_salas_optimas(
        bloque_id=solicitud.bloque_id,
        aforo_esperado=solicitud.aforo_esperado,
        necesita_proyector=solicitud.necesita_proyector,
        necesita_enchufes=solicitud.necesita_enchufes
    )

    # 4. Formatear la respuesta para el Frontend
    if not salas_optimas:
        return {"mensaje": "No se encontraron salas que cumplan los requisitos.", "salas_sugeridas": []}

    return {"mensaje": "Salas encontradas con éxito.", "salas_sugeridas": salas_optimas}


@app.post("/api/asignar", response_model=schemas.AsignacionResponse)
def confirmar_asignacion(confirmacion: schemas.ConfirmacionAsignacion, db: Session = Depends(get_db)):
    """
    Recibe la confirmación del Coordinador y guarda la asignación en la BD.
    """
    sala_repo = SalaRepositorySQL(db)
    asignacion_repo = AsignacionRepositorySQL(db)
    bloque_repo = BloqueHorarioRepositorySQL(db)

    use_case = AsignacionUseCase(sala_repo, asignacion_repo, bloque_repo)

    try:
        # Ejecutamos el caso de uso
        asignacion = use_case.confirmar_asignacion(
            seccion_id=confirmacion.seccion_id,
            sala_id=confirmacion.sala_id,
            bloque_id=confirmacion.bloque_id,
            coordinador_id=confirmacion.coordinador_id
        )
        return asignacion
    except Exception as e:
        # Si Camilo o Lucas lanzan un error (ej. sala ya ocupada), devolvemos un Error 400 a la web
        raise HTTPException(status_code=400, detail=str(e))