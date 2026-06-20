# ─────────────────────────────────────────────
# routers/consultas.py — Rotas de consultas
# ─────────────────────────────────────────────

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, services
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


# GET /consultas/{id}/cobranca — calcula preço/duração via regras de negócio
@router.get("/{consulta_id}/cobranca")
def cobranca_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return {
        "tipo": consulta.tipo,
        "preco": services.calcular_preco(consulta.tipo),
        "duracao_minutos": services.calcular_duracao_minutos(consulta.tipo),
        "hora_inicio": consulta.hora,
        "hora_fim": services.calcular_fim(
            services.validar_formato_hora(consulta.hora), consulta.tipo
        ).strftime("%H:%M"),
    }


# POST /consultas — cria uma nova consulta
@router.post("/", response_model=schemas.ConsultaOut, status_code=201)
def criar_consulta(dados: schemas.ConsultaCreate, db: Session = Depends(get_db)):
    # Médico existe?
    medico = db.query(models.Medico).filter(models.Medico.id == dados.medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    # Regras de negócio (formato/horário/antecedência/email/tipo)
    try:
        services.validar_agendamento(
            data_str=dados.data,
            hora_str=dados.hora,
            tipo=dados.tipo,
            horario_medico=medico.horario,
            email=dados.email or None,
        )
    except services.RegraNegocioError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Conflito de horário com o médico
    conflito = db.query(models.Consulta).filter(
        models.Consulta.medico_id == dados.medico_id,
        models.Consulta.data      == dados.data,
        models.Consulta.hora      == dados.hora
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail=f"Horário {dados.hora} já está ocupado nesta data")

    # Paciente não pode ter 2 consultas no mesmo dia
    duplicada_paciente = db.query(models.Consulta).filter(
        models.Consulta.nome == dados.nome,
        models.Consulta.data == dados.data,
    ).first()
    if duplicada_paciente:
        raise HTTPException(
            status_code=400,
            detail="Paciente já possui consulta agendada neste dia",
        )

    # Limite diário por médico
    qtd_no_dia = db.query(models.Consulta).filter(
        models.Consulta.medico_id == dados.medico_id,
        models.Consulta.data == dados.data,
    ).count()
    if qtd_no_dia >= services.MAX_CONSULTAS_POR_MEDICO_POR_DIA:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Médico já atingiu o limite de "
                f"{services.MAX_CONSULTAS_POR_MEDICO_POR_DIA} consultas neste dia"
            ),
        )

    # Retorno: precisa de consulta anterior do mesmo paciente com o mesmo médico
    if dados.tipo == "retorno":
        nova_data = services.validar_formato_data(dados.data)
        limite = nova_data - timedelta(days=services.JANELA_RETORNO_DIAS)
        consulta_anterior = (
            db.query(models.Consulta)
            .filter(
                models.Consulta.medico_id == dados.medico_id,
                models.Consulta.nome == dados.nome,
                models.Consulta.tipo == "consulta",
                models.Consulta.data >= limite.isoformat(),
                models.Consulta.data < dados.data,
            )
            .order_by(models.Consulta.data.desc())
            .first()
        )
        try:
            services.validar_retorno_tem_consulta_previa(
                services.validar_formato_data(consulta_anterior.data) if consulta_anterior else None,
                nova_data,
            )
        except services.RegraNegocioError as e:
            raise HTTPException(status_code=400, detail=str(e))

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

    nova_data = dados.data or consulta.data
    nova_hora = dados.hora or consulta.hora
    novo_tipo = dados.tipo or consulta.tipo

    # Se mudou algo relevante, revalida regras
    if dados.data or dados.hora or dados.tipo or dados.email:
        medico = db.query(models.Medico).filter(models.Medico.id == consulta.medico_id).first()
        try:
            services.validar_agendamento(
                data_str=nova_data,
                hora_str=nova_hora,
                tipo=novo_tipo,
                horario_medico=medico.horario if medico else None,
                email=(dados.email if dados.email is not None else consulta.email) or None,
            )
        except services.RegraNegocioError as e:
            raise HTTPException(status_code=400, detail=str(e))

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
