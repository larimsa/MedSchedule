# ─────────────────────────────────────────────
# schemas.py — Validação de dados (Pydantic)
# ─────────────────────────────────────────────

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


# ── MÉDICO ──────────────────────────────────

class MedicoBase(BaseModel):
    nome:          str
    crm:           str
    especialidade: str
    email:         str
    telefone:      Optional[str] = ""
    endereco:      Optional[str] = ""
    horario:       Optional[str] = ""
    cor:           Optional[int] = 0


class MedicoCreate(MedicoBase):
    pass


class MedicoUpdate(BaseModel):
    nome:          Optional[str] = None
    crm:           Optional[str] = None
    especialidade: Optional[str] = None
    email:         Optional[str] = None
    telefone:      Optional[str] = None
    endereco:      Optional[str] = None
    horario:       Optional[str] = None
    cor:           Optional[int] = None


class MedicoOut(MedicoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── CONSULTA ────────────────────────────────

class ConsultaBase(BaseModel):
    medico_id:   int
    nome:        str
    email:       Optional[str] = ""
    telefone:    Optional[str] = ""
    data:        str
    hora:        str
    tipo:        str
    observacoes: Optional[str] = ""


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(BaseModel):
    nome:        Optional[str] = None
    email:       Optional[str] = None
    telefone:    Optional[str] = None
    data:        Optional[str] = None
    hora:        Optional[str] = None
    tipo:        Optional[str] = None
    observacoes: Optional[str] = None


class ConsultaOut(ConsultaBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
