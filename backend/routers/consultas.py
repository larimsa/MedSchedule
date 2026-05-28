# ─────────────────────────────────────────────
# routers/consultas.py — Rotas de consultas
# ─────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas
from database import get_db

router = APIRouter(prefix="/consultas", tags=["Consultas"])


# GET /consultas — lista consultas, com filtros opcionais
@router.get("/", response_model=List[schemas.ConsultaOut])
def listar_consultas(
    medico_id: Optional[int] = None,
    data:      Optional[str] = None,
    tipo:      Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Consulta)

    if medico_id:
        query = query.filter(models.Consulta.medico_id == medico_id)
    if data:
        query = query.filter(models.Consulta.data == data)
    if tipo:
        query = query.filter(models.Consulta.tipo == tipo)

    return query.order_by(models.Consulta.data, models.Consulta.hora).all()


# GET /consultas/{id} — busca uma consulta pelo ID
@router.get("/{consulta_id}", response_model=schemas.ConsultaOut)
def buscar_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return consulta


# POST /consultas — cria uma nova consulta
@router.post("/", response_model=schemas.ConsultaOut, status_code=201)
def criar_consulta(dados: schemas.ConsultaCreate, db: Session = Depends(get_db)):
    # Verifica se médico existe
    medico = db.query(models.Medico).filter(models.Medico.id == dados.medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    # Verifica conflito de horário
    conflito = db.query(models.Consulta).filter(
        models.Consulta.medico_id == dados.medico_id,
        models.Consulta.data      == dados.data,
        models.Consulta.hora      == dados.hora
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail=f"Horário {dados.hora} já está ocupado nesta data")

    consulta = models.Consulta(**dados.model_dump())
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


# PUT /consultas/{id} — atualiza dados de uma consulta
@router.put("/{consulta_id}", response_model=schemas.ConsultaOut)
def atualizar_consulta(consulta_id: int, dados: schemas.ConsultaUpdate, db: Session = Depends(get_db)):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    # Se mudou data/hora, verifica conflito
    nova_data = dados.data or consulta.data
    nova_hora = dados.hora or consulta.hora

    if nova_data != consulta.data or nova_hora != consulta.hora:
        conflito = db.query(models.Consulta).filter(
            models.Consulta.medico_id == consulta.medico_id,
            models.Consulta.data      == nova_data,
            models.Consulta.hora      == nova_hora,
            models.Consulta.id        != consulta_id
        ).first()
        if conflito:
            raise HTTPException(status_code=400, detail=f"Horário {nova_hora} já está ocupado nesta data")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(consulta, campo, valor)

    db.commit()
    db.refresh(consulta)
    return consulta


# DELETE /consultas/{id} — remove uma consulta
@router.delete("/{consulta_id}", status_code=204)
def deletar_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    db.delete(consulta)
    db.commit()
