from crear_db import SessionLocal, Sala, init_db

salas = [
    {"codigo": "A-101", "capacidad": 20, "estado": "DISPONIBLE",  "proyector_ok": True,  "enchufes_usables": 0},
    {"codigo": "A-102", "capacidad": 25, "estado": "DISPONIBLE", "proyector_ok": False, "enchufes_usables": 4},
    {"codigo": "A-103", "capacidad": 30, "estado": "MANTENIMIENTO", "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "A-201", "capacidad": 35, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 8},
    {"codigo": "A-202", "capacidad": 40, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 6},
    {"codigo": "A-203", "capacidad": 45, "estado": "ASIGNADA", "proyector_ok": True,  "enchufes_usables": 10},
    {"codigo": "B-101", "capacidad": 22, "estado": "DISPONIBLE", "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "B-102", "capacidad": 28, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 2},
    {"codigo": "B-103", "capacidad": 33, "estado": "MANTENIMIENTO", "proyector_ok": False, "enchufes_usables": 0},
    {"codigo": "B-201", "capacidad": 38, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 12},
    {"codigo": "B-202", "capacidad": 42, "estado": "ASIGNADA", "proyector_ok": False, "enchufes_usables": 5},
    {"codigo": "C-101", "capacidad": 24, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 0},
    {"codigo": "C-102", "capacidad": 31, "estado": "DISPONIBLE", "proyector_ok": False, "enchufes_usables": 8},
    {"codigo": "C-201", "capacidad": 37, "estado": "DISPONIBLE", "proyector_ok": True,  "enchufes_usables": 6},
    {"codigo": "C-202", "capacidad": 45, "estado": "ASIGNADA", "proyector_ok": True,  "enchufes_usables": 4},
]
 
def seed():
    #crea tablas y conexión
    init_db()
    db = SessionLocal()
 
    #intenta crear datos de salas
    try:
        for datos in salas:
            sala = Sala(**datos)
            db.add(sala)

        #los añade y confirma que se hizo
        db.commit()
        print(f"{len(salas)} salas insertadas correctamente.\n")
 
    #informa si hubo error y destruye los datos que se hayan hecho
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()
 
if __name__ == "__main__":
    seed()