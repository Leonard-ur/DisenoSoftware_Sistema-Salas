# backend/infrastructure/seed_completo.py
#
# Ejecutar desde la carpeta backend/:
#   python infrastructure/seed_completo.py
#
# Este script:
#   1. Crea todas las tablas (si no existen)
#   2. Pobla: salas, bloques_horario, usuarios, secciones y asignaciones de ejemplo

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time, datetime
from infrastructure.crear_db import (
    SessionLocal, init_db,
    Sala, BloqueHorario, Usuario, Seccion, Asignacion
)

# ──────────────────────────────────────────────
# DATOS DE PRUEBA
# ──────────────────────────────────────────────

SALAS = [
    {"codigo": "A-101", "capacidad": 20, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 0},
    {"codigo": "A-102", "capacidad": 25, "estado": "DISPONIBLE",    "proyector_ok": False, "enchufes_usables": 4},
    {"codigo": "A-103", "capacidad": 30, "estado": "MANTENIMIENTO", "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "A-201", "capacidad": 35, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 8},
    {"codigo": "A-202", "capacidad": 40, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 6},
    {"codigo": "A-203", "capacidad": 45, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 10},
    {"codigo": "B-101", "capacidad": 22, "estado": "DISPONIBLE",    "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "B-102", "capacidad": 28, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 2},
    {"codigo": "B-103", "capacidad": 33, "estado": "MANTENIMIENTO", "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "B-201", "capacidad": 38, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 12},
    {"codigo": "B-202", "capacidad": 42, "estado": "DISPONIBLE",    "proyector_ok": False, "enchufes_usables": 5},
    {"codigo": "C-101", "capacidad": 24, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 0},
    {"codigo": "C-102", "capacidad": 31, "estado": "DISPONIBLE",    "proyector_ok": False, "enchufes_usables": 8},
    {"codigo": "C-201", "capacidad": 37, "estado": "DISPONIBLE",    "proyector_ok": True,  "enchufes_usables": 6},
    {"codigo": "C-202", "capacidad": 45, "estado": "MANTENIMIENTO", "proyector_ok": True,  "enchufes_usables": 4},
]

# Bloques: Lunes a Viernes, 4 bloques por día
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
FRANJAS = [
    (time(8, 30),  time(10, 0)),
    (time(10, 15), time(11, 45)),
    (time(14, 0),  time(15, 30)),
    (time(15, 45), time(17, 15)),
]

USUARIOS = [
    {"nombre": "Marta Gómez",    "email": "mgomez@uct.cl",   "rol": "COORDINADOR"},
    {"nombre": "Dr. Roberto Silva", "email": "rsilva@uct.cl", "rol": "DOCENTE"},
    {"nombre": "Dra. Ana Torres",   "email": "atorres@uct.cl","rol": "DOCENTE"},
]

SECCIONES = [
    {"codigo": "INFO-045-1-2025-1", "aforo_inscrito": 45, "necesita_proyector": True,  "necesita_enchufes": False, "docente_idx": 1},
    {"codigo": "INFO-030-1-2025-1", "aforo_inscrito": 30, "necesita_proyector": False, "necesita_enchufes": True,  "docente_idx": 1},
    {"codigo": "INFO-020-1-2025-1", "aforo_inscrito": 22, "necesita_proyector": True,  "necesita_enchufes": True,  "docente_idx": 2},
]

# ──────────────────────────────────────────────
# FUNCIONES DE SEED
# ──────────────────────────────────────────────

def seed_salas(db):
    if db.query(Sala).count() > 0:
        print("  [SKIP] Salas ya existen.")
        return []
    objetos = [Sala(**d) for d in SALAS]
    db.add_all(objetos)
    db.flush()  # para obtener IDs sin hacer commit aún
    print(f"  [OK]   {len(objetos)} salas insertadas.")
    return objetos

def seed_bloques(db):
    if db.query(BloqueHorario).count() > 0:
        print("  [SKIP] Bloques horarios ya existen.")
        return []
    objetos = []
    for dia in DIAS:
        for inicio, fin in FRANJAS:
            objetos.append(BloqueHorario(dia_semana=dia, hora_inicio=inicio, hora_fin=fin))
    db.add_all(objetos)
    db.flush()
    print(f"  [OK]   {len(objetos)} bloques horarios insertados ({len(DIAS)} días × {len(FRANJAS)} franjas).")
    return objetos

def seed_usuarios(db):
    if db.query(Usuario).count() > 0:
        print("  [SKIP] Usuarios ya existen.")
        return []
    objetos = [Usuario(**u) for u in USUARIOS]
    db.add_all(objetos)
    db.flush()
    print(f"  [OK]   {len(objetos)} usuarios insertados.")
    return objetos

def seed_secciones(db):
    if db.query(Seccion).count() > 0:
        print("  [SKIP] Secciones ya existen.")
        return []

    # Recuperar IDs reales de docentes
    docentes = db.query(Usuario).filter(Usuario.rol == "DOCENTE").order_by(Usuario.id).all()
    if not docentes:
        print("  [WARN] No hay docentes en la BD; secciones omitidas.")
        return []

    objetos = []
    for s in SECCIONES:
        docente_real = docentes[min(s["docente_idx"] - 1, len(docentes) - 1)]
        objetos.append(Seccion(
            codigo=s["codigo"],
            aforo_inscrito=s["aforo_inscrito"],
            necesita_proyector=s["necesita_proyector"],
            necesita_enchufes=s["necesita_enchufes"],
            docente_id=docente_real.id,
        ))
    db.add_all(objetos)
    db.flush()
    print(f"  [OK]   {len(objetos)} secciones insertadas.")
    return objetos

def seed_asignaciones(db):
    if db.query(Asignacion).count() > 0:
        print("  [SKIP] Asignaciones ya existen.")
        return

    coordinador = db.query(Usuario).filter(Usuario.rol == "COORDINADOR").first()
    secciones   = db.query(Seccion).all()
    salas       = db.query(Sala).filter(Sala.estado == "DISPONIBLE").order_by(Sala.capacidad.desc()).all()
    bloques     = db.query(BloqueHorario).all()

    if not (coordinador and secciones and salas and bloques):
        print("  [WARN] Faltan datos previos; asignaciones omitidas.")
        return

    asignaciones_ejemplo = [
        # (seccion_idx, sala_idx, bloque_idx)
        (0, 0, 0),   # Sección 1 → sala más grande → bloque Lunes 08:30
        (1, 2, 1),   # Sección 2 → sala mediana   → bloque Lunes 10:15
        (2, 4, 5),   # Sección 3 → otra sala       → bloque Martes 14:00
    ]

    creadas = 0
    for sec_i, sala_i, bloque_i in asignaciones_ejemplo:
        if sec_i >= len(secciones) or sala_i >= len(salas) or bloque_i >= len(bloques):
            continue
        db.add(Asignacion(
            seccion_id=secciones[sec_i].id,
            sala_id=salas[sala_i].id,
            bloque_id=bloques[bloque_i].id,
            confirmado_por=coordinador.id,
            estado="CONFIRMADA",
            creado_en=datetime.utcnow(),
        ))
        creadas += 1

    print(f"  [OK]   {creadas} asignaciones de ejemplo insertadas.")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def run():
    print("\n=== INICIALIZANDO BASE DE DATOS ===")
    init_db()
    print("  [OK]   Tablas verificadas / creadas.\n")

    db = SessionLocal()
    try:
        print("=== INSERTANDO DATOS ===")
        seed_salas(db)
        seed_bloques(db)
        seed_usuarios(db)
        seed_secciones(db)
        seed_asignaciones(db)
        db.commit()
        print("\n=== LISTO ===")
        print("Base de datos lista. Ahora levanta el servidor:\n")
        print("  cd backend")
        print("  uvicorn main:app --reload\n")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()
