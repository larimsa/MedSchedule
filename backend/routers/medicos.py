# ─────────────────────────────────────────────
# routers/medicos.py — Rotas de médicos
# ─────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db

router = APIRouter(prefix="/medicos", tags=["Médicos"])


# GET /medicos — lista todos os médicos
@router.get("/", response_model=List[schemas.MedicoOut])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).all()


# GET /medicos/{id} — busca um médico pelo ID
@router.get("/{medico_id}", response_model=schemas.MedicoOut)
def buscar_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico


# POST /medicos — cria um novo médico
@router.post("/", response_model=schemas.MedicoOut, status_code=201)
def criar_medico(dados: schemas.MedicoCreate, db: Session = Depends(get_db)):
    # Verifica CRM duplicado
    existente = db.query(models.Medico).filter(models.Medico.crm == dados.crm).first()
    if existente:
        raise HTTPException(status_code=400, detail="CRM já cadastrado")

    medico = models.Medico(**dados.model_dump())
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


# PUT /medicos/{id} — atualiza dados de um médico
@router.put("/{medico_id}", response_model=schemas.MedicoOut)
def atualizar_medico(medico_id: int, dados: schemas.MedicoUpdate, db: Session = Depends(get_db)):
    medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(medico, campo, valor)

    db.commit()
    db.refresh(medico)
    return medico


# DELETE /medicos/{id} — remove um médico e suas consultas
@router.delete("/{medico_id}", status_code=204)
def deletar_medico(medico_id: int, db: Session = Depends(get_db)):
    medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    db.delete(medico)
    db.commit()
