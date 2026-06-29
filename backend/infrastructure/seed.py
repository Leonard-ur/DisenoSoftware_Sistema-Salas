# infrastructure/seed.py
#
# Run from the backend/ folder:
#   python infrastructure/seed.py
#
# This script:
#   1. Creates every table (if missing).
#   2. Seeds rooms, time blocks, users, sections and sample assignments.

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, time, timezone  # noqa: E402

from infrastructure.database import (  # noqa: E402
    Assignment,
    Room,
    Section,
    SessionLocal,
    TimeBlock,
    User,
    init_db,
)

# ──────────────────────────────────────────────
# TEST DATA
# ──────────────────────────────────────────────

# (code, capacity, status, has_projector, usable_outlets, is_accessible, tags)
ROOMS = [
    ("A-101", 20, "DISPONIBLE",    True,  0,  True,  None),
    ("A-102", 25, "DISPONIBLE",    False, 4,  False, "computacion"),
    ("A-103", 30, "MANTENIMIENTO", False, 0,  False, None),
    ("A-201", 35, "DISPONIBLE",    True,  8,  True,  None),
    ("A-202", 40, "DISPONIBLE",    True,  6,  False, "computacion"),
    ("A-203", 45, "DISPONIBLE",    True,  10, True,  "computacion"),
    ("B-101", 22, "DISPONIBLE",    False, 0,  False, None),
    ("B-102", 28, "DISPONIBLE",    True,  2,  True,  None),
    ("B-103", 33, "MANTENIMIENTO", False, 0,  False, None),
    ("B-201", 38, "DISPONIBLE",    True,  12, True,  "computacion"),
    ("B-202", 42, "DISPONIBLE",    False, 5,  False, None),
    ("C-101", 24, "DISPONIBLE",    True,  0,  False, None),
    ("C-102", 31, "DISPONIBLE",    False, 8,  True,  "computacion"),
    ("C-201", 37, "DISPONIBLE",    True,  6,  False, None),
    ("C-202", 45, "MANTENIMIENTO", True,  4,  False, None),
]

# Monday to Friday, 4 blocks per day (weekday values stay in Spanish).
WEEKDAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
TIME_RANGES = [
    (time(8, 30), time(10, 0)),
    (time(10, 15), time(11, 45)),
    (time(14, 0), time(15, 30)),
    (time(15, 45), time(17, 15)),
]

# (name, email, role)
USERS = [
    ("Marta Gómez", "mgomez@uct.cl", "COORDINADOR"),
    ("Dr. Roberto Silva", "rsilva@uct.cl", "DOCENTE"),
    ("Dra. Ana Torres", "atorres@uct.cl", "DOCENTE"),
]

# (code, enrolled_count, requires_projector, requires_outlets, teacher_idx)
SECTIONS = [
    ("INFO-045-1-2025-1", 45, True, False, 1),
    ("INFO-030-1-2025-1", 30, False, True, 1),
    ("INFO-020-1-2025-1", 22, True, True, 2),
]

# (section_idx, room_idx, block_idx)
SAMPLE_ASSIGNMENTS = [
    (0, 0, 0),
    (1, 2, 1),
    (2, 4, 5),
]

# ──────────────────────────────────────────────
# SEED FUNCTIONS
# ──────────────────────────────────────────────


def seed_rooms(db):
    if db.query(Room).count() > 0:
        print("  [SKIP] Rooms already exist.")
        return
    db.add_all(
        Room(
            code=code,
            capacity=capacity,
            status=status,
            has_projector=has_projector,
            usable_outlets=usable_outlets,
            is_accessible=is_accessible,
            tags=tags,
        )
        for code, capacity, status, has_projector, usable_outlets, is_accessible, tags in ROOMS
    )
    db.flush()
    print(f"  [OK]   {len(ROOMS)} rooms inserted.")


def seed_time_blocks(db):
    if db.query(TimeBlock).count() > 0:
        print("  [SKIP] Time blocks already exist.")
        return
    blocks = [
        TimeBlock(weekday=weekday, start_time=start, end_time=end)
        for weekday in WEEKDAYS
        for start, end in TIME_RANGES
    ]
    db.add_all(blocks)
    db.flush()
    print(f"  [OK]   {len(blocks)} time blocks inserted.")


def seed_users(db):
    if db.query(User).count() > 0:
        print("  [SKIP] Users already exist.")
        return
    db.add_all(
        User(name=name, email=email, role=role)
        for name, email, role in USERS
    )
    db.flush()
    print(f"  [OK]   {len(USERS)} users inserted.")


def seed_sections(db):
    if db.query(Section).count() > 0:
        print("  [SKIP] Sections already exist.")
        return
    teachers = (
        db.query(User)
        .filter(User.role == "DOCENTE")
        .order_by(User.id)
        .all()
    )
    if not teachers:
        print("  [WARN] No teachers in the database; sections skipped.")
        return
    db.add_all(_build_section(row, teachers) for row in SECTIONS)
    db.flush()
    print(f"  [OK]   {len(SECTIONS)} sections inserted.")


def _build_section(row, teachers):
    code, enrolled_count, requires_projector, requires_outlets, teacher_idx = row
    teacher = teachers[min(teacher_idx - 1, len(teachers) - 1)]
    return Section(
        code=code,
        enrolled_count=enrolled_count,
        requires_projector=requires_projector,
        requires_outlets=requires_outlets,
        teacher_id=teacher.id,
    )


def seed_assignments(db):
    if db.query(Assignment).count() > 0:
        print("  [SKIP] Assignments already exist.")
        return
    coordinator = db.query(User).filter(User.role == "COORDINADOR").first()
    sections = db.query(Section).all()
    rooms = (
        db.query(Room)
        .filter(Room.status == "DISPONIBLE")
        .order_by(Room.capacity.desc())
        .all()
    )
    blocks = db.query(TimeBlock).all()
    if not (coordinator and sections and rooms and blocks):
        print("  [WARN] Missing prerequisite data; assignments skipped.")
        return
    created = _create_sample_assignments(
        db, coordinator, sections, rooms, blocks
    )
    print(f"  [OK]   {created} sample assignments inserted.")


def _create_sample_assignments(db, coordinator, sections, rooms, blocks):
    created = 0
    for section_i, room_i, block_i in SAMPLE_ASSIGNMENTS:
        if not _indices_in_range(section_i, room_i, block_i, sections, rooms, blocks):
            continue
        db.add(
            Assignment(
                section_id=sections[section_i].id,
                room_id=rooms[room_i].id,
                time_block_id=blocks[block_i].id,
                confirmed_by=coordinator.id,
                status="CONFIRMADA",
                created_at=datetime.now(timezone.utc),
            )
        )
        created += 1
    return created


def _indices_in_range(section_i, room_i, block_i, sections, rooms, blocks):
    return (
        section_i < len(sections)
        and room_i < len(rooms)
        and block_i < len(blocks)
    )


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────


def run():
    print("\n=== INITIALIZING DATABASE ===")
    init_db()
    print("  [OK]   Tables verified / created.\n")

    db = SessionLocal()
    try:
        print("=== INSERTING DATA ===")
        seed_rooms(db)
        seed_time_blocks(db)
        seed_users(db)
        seed_sections(db)
        seed_assignments(db)
        db.commit()
        _print_success()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _print_success():
    print("\n=== DONE ===")
    print("Database ready. Now start the server:\n")
    print("  cd backend")
    print("  uvicorn main:app --reload\n")


if __name__ == "__main__":
    run()