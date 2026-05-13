import sys
import os
# Esto le dice a Python que la carpeta raíz del proyecto es la que está un nivel más arriba.
# Así podrá encontrar las carpetas 'domain', 'use_cases', etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean,
    Time, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

#configuraciones iniciales
DATABASE_URL = "sqlite:///./salas.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} 
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

#crear tablas
class Sala(Base):
    __tablename__ = "sala"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    capacidad = Column(Integer, nullable=False)
    #hay 3 posibles estados: disponible / asignada / mantenimiento
    estado  = Column(String(20), nullable=False, default="DISPONIBLE")
    proyector_ok = Column(Boolean, nullable=False, default=False)
    # True = proyector en buen estado / False = en mal estado o no tiene
    enchufes_usables = Column(Integer, nullable=False, default=0)
    # Cantidad de enchufes funcionales

    asignaciones = relationship("Asignacion", back_populates="sala")

    def __repr__(self):
        return f"<Sala {self.codigo} | cap={self.capacidad} | {self.estado}>"


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    #docetne / coordinador
    rol = Column(String(20), nullable=False)
    secciones = relationship("Seccion", back_populates="docente")
    asignaciones_confirm = relationship("Asignacion", back_populates="coordinador")

    def __repr__(self):
        return f"<Usuario {self.nombre} | {self.rol}>"


class Seccion(Base):
    __tablename__ = "seccion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    #ej: INFO1156-2-2026-1
    codigo = Column(String(30), unique=True, nullable=False)
    aforo_inscrito = Column(Integer, nullable=False)
    necesita_proyector = Column(Boolean, nullable=False, default=False)
    necesita_enchufes = Column(Boolean, nullable=False, default=False)
    docente_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)

    docente = relationship("Usuario", back_populates="secciones")
    asignaciones = relationship("Asignacion", back_populates="seccion")

    def __repr__(self):
        return f"<Seccion {self.codigo} | aforo={self.aforo_inscrito}>"


class BloqueHorario(Base):
    __tablename__ = "bloque_horario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(String(10), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    asignaciones = relationship("Asignacion", back_populates="bloque")

    def __repr__(self):
        return f"<Bloque {self.dia_semana} {self.hora_inicio}-{self.hora_fin}>"


class Asignacion(Base):
    __tablename__ = "asignacion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seccion_id = Column(Integer, ForeignKey("seccion.id"), nullable=False)
    sala_id = Column(Integer, ForeignKey("sala.id"), nullable=False)
    bloque_id = Column(Integer, ForeignKey("bloque_horario.id"), nullable=False)
    estado = Column(String(20), nullable=False, default="CONFIRMADA")
    # CONFIRMADA | LIBERADA
    confirmado_por = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    #esto evita que se pueda ocupar la misma sala en el mismo bloque horario
    __table_args__ = (
        UniqueConstraint("sala_id", "bloque_id", name="idx_sala_bloque"),
    )

    seccion = relationship("Seccion", back_populates="asignaciones")
    sala = relationship("Sala", back_populates="asignaciones")
    bloque = relationship("BloqueHorario", back_populates="asignaciones")
    coordinador = relationship("Usuario", back_populates="asignaciones_confirm")

    def __repr__(self):
        return f"<Asignacion seccion={self.seccion_id} sala={self.sala_id} bloque={self.bloque_id}>"


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Base de datos creada: salas.db")

