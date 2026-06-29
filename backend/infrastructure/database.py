# infrastructure/database.py

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./salas.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    # Three possible values: DISPONIBLE / ASIGNADA / MANTENIMIENTO
    status = Column(String(20), nullable=False, default="DISPONIBLE")
    # True = working projector / False = broken or none
    has_projector = Column(Boolean, nullable=False, default=False)
    # Number of working power outlets
    usable_outlets = Column(Integer, nullable=False, default=0)
    # True = room meets universal accessibility standards
    is_accessible = Column(Boolean, default=False)
    # Optional category tags (e.g. "computacion", "laboratorio")
    tags = Column(String(100), nullable=True)

    assignments = relationship("Assignment", back_populates="room")

    def __repr__(self) -> str:
        return f"<Room {self.code} | cap={self.capacity} | {self.status}>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    # DOCENTE / COORDINADOR
    role = Column(String(20), nullable=False)

    sections = relationship("Section", back_populates="teacher")
    confirmed_assignments = relationship(
        "Assignment", back_populates="coordinator"
    )

    def __repr__(self) -> str:
        return f"<User {self.name} | {self.role}>"


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # e.g. INFO1156-2-2026-1
    code = Column(String(30), unique=True, nullable=False)
    enrolled_count = Column(Integer, nullable=False)
    requires_projector = Column(Boolean, nullable=False, default=False)
    requires_outlets = Column(Boolean, nullable=False, default=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    teacher = relationship("User", back_populates="sections")
    assignments = relationship("Assignment", back_populates="section")

    def __repr__(self) -> str:
        return f"<Section {self.code} | enrolled={self.enrolled_count}>"


class TimeBlock(Base):
    __tablename__ = "time_blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    weekday = Column(String(10), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    assignments = relationship("Assignment", back_populates="time_block")

    def __repr__(self) -> str:
        return f"<TimeBlock {self.weekday} {self.start_time}-{self.end_time}>"


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    time_block_id = Column(
        Integer, ForeignKey("time_blocks.id"), nullable=False
    )
    # CONFIRMADA | LIBERADA
    status = Column(String(20), nullable=False, default="CONFIRMADA")
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_utc_now)

    # Prevents booking the same room in the same time block twice.
    __table_args__ = (
        UniqueConstraint("room_id", "time_block_id", name="uq_room_time_block"),
    )

    section = relationship("Section", back_populates="assignments")
    room = relationship("Room", back_populates="assignments")
    time_block = relationship("TimeBlock", back_populates="assignments")
    coordinator = relationship("User", back_populates="confirmed_assignments")

    def __repr__(self) -> str:
        return (
            f"<Assignment section={self.section_id} "
            f"room={self.room_id} block={self.time_block_id}>"
        )


def init_db() -> None:
    """Create every table in the configured database."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database created: salas.db")
