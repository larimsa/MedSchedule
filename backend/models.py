# ─────────────────────────────────────────────
# models.py — Tabelas do banco de dados (SQLAlchemy)
# ─────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id         = Column(Integer, primary_key=True, index=True)
    nome       = Column(String, nullable=False)
    crm        = Column(String, nullable=False, unique=True)
    especialidade = Column(String, nullable=False)
    email      = Column(String, nullable=False)
    telefone   = Column(String)
    endereco   = Column(String)
    horario    = Column(String)
    cor        = Column(Integer, default=0)

    consultas  = relationship("Consulta", back_populates="medico", cascade="all, delete")


class Consulta(Base):
    __tablename__ = "consultas"

    id         = Column(Integer, primary_key=True, index=True)
    medico_id  = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    nome       = Column(String, nullable=False)
    email      = Column(String)
    telefone   = Column(String)
    data       = Column(String, nullable=False)   # formato: "YYYY-MM-DD"
    hora       = Column(String, nullable=False)   # formato: "HH:MM"
    tipo       = Column(String, nullable=False)   # consulta | retorno | exame
    observacoes = Column(String, default="")

    medico     = relationship("Medico", back_populates="consultas")
