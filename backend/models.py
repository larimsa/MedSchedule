# ─────────────────────────────────────────────
# models.py — Tabelas do banco de dados (SQLAlchemy)
# ─────────────────────────────────────────────

from sqlalchemy import (
    Column, Integer, String, ForeignKey, CheckConstraint, DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id            = Column(Integer, primary_key=True, index=True)
    nome          = Column(String, nullable=False)
    crm           = Column(String, nullable=False, unique=True)
    especialidade = Column(String, nullable=False)
    email         = Column(String, nullable=False)
    telefone      = Column(String)
    endereco      = Column(String)
    horario       = Column(String)
    cor           = Column(Integer, default=0)

    # Timestamps de auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    consultas = relationship("Consulta", back_populates="medico", cascade="all, delete")


class Consulta(Base):
    __tablename__ = "consultas"

    id          = Column(Integer, primary_key=True, index=True)
    medico_id   = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    nome        = Column(String, nullable=False)
    email       = Column(String)
    telefone    = Column(String)
    data        = Column(String, nullable=False)   # "YYYY-MM-DD"
    hora        = Column(String, nullable=False)   # "HH:MM"
    tipo        = Column(String, nullable=False)
    observacoes = Column(String, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Restrição em nível de banco: tipo só pode ser um dos três
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('consulta','retorno','exame')",
            name="ck_consulta_tipo_valido",
        ),
    )

    medico = relationship("Medico", back_populates="consultas")
