# ─────────────────────────────────────────────
# services.py — Regras de negócio (puras, testáveis sem DB)
# ─────────────────────────────────────────────

import re
from datetime import datetime, date, time, timedelta
from typing import Optional


# ── CONSTANTES DE NEGÓCIO ────────────────────

TIPOS_VALIDOS = {"consulta", "retorno", "exame"}

HORARIO_ABERTURA = time(8, 0)
HORARIO_FECHAMENTO = time(18, 0)
INTERVALO_MINUTOS = 30

ANTECEDENCIA_MINIMA_MINUTOS = 60
MAX_CONSULTAS_POR_MEDICO_POR_DIA = 16
JANELA_RETORNO_DIAS = 30

PRECO_DURACAO = {
    "consulta": {"preco": 200.0, "duracao_min": 30},
    "retorno":  {"preco": 0.0,   "duracao_min": 15},
    "exame":    {"preco": 350.0, "duracao_min": 45},
}


# ── EXCEÇÃO DE REGRA DE NEGÓCIO ──────────────

class RegraNegocioError(Exception):
    """Erro de regra de negócio (vira HTTP 400 nos routers)."""


# ── VALIDAÇÕES DE FORMATO ────────────────────

RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_HORA = re.compile(r"^\d{2}:\d{2}$")
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_RE_CRM_FORMAL = re.compile(r"^CRM/[A-Z]{2}\s\d{4,6}$")
_RE_CRM_TRACO = re.compile(r"^\d{4,6}-[A-Z]{2}$")
_RE_CRM_SIMPLES = re.compile(r"^\d{4,6}$")


def validar_formato_data(s: str) -> date:
    if not s or not RE_DATA.match(s):
        raise RegraNegocioError("Data deve estar no formato YYYY-MM-DD")
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise RegraNegocioError("Data inválida")


def validar_formato_hora(s: str) -> time:
    if not s or not RE_HORA.match(s):
        raise RegraNegocioError("Hora deve estar no formato HH:MM")
    try:
        return datetime.strptime(s, "%H:%M").time()
    except ValueError:
        raise RegraNegocioError("Hora inválida")


def validar_email(s: str) -> None:
    if not s or not RE_EMAIL.match(s):
        raise RegraNegocioError("Email inválido")


def validar_crm(s: str) -> None:
    """Aceita: 'CRM/SP 123456', '123456-SP' ou '123456'."""
    if not s:
        raise RegraNegocioError("CRM é obrigatório")
    s = s.strip().upper()
    if not (_RE_CRM_FORMAL.match(s) or _RE_CRM_TRACO.match(s) or _RE_CRM_SIMPLES.match(s)):
        raise RegraNegocioError("CRM inválido (use 'CRM/UF NNNNNN' ou 'NNNNNN-UF')")


def validar_tipo(tipo: str) -> None:
    if tipo not in TIPOS_VALIDOS:
        raise RegraNegocioError(
            f"Tipo inválido. Use: {', '.join(sorted(TIPOS_VALIDOS))}"
        )


# ── REGRAS DE AGENDAMENTO ────────────────────

def validar_horario_comercial(h: time) -> None:
    if h < HORARIO_ABERTURA or h >= HORARIO_FECHAMENTO:
        raise RegraNegocioError(
            f"Horário fora do expediente ({HORARIO_ABERTURA.strftime('%H:%M')}"
            f"–{HORARIO_FECHAMENTO.strftime('%H:%M')})"
        )


def validar_intervalo(h: time) -> None:
    if h.minute % INTERVALO_MINUTOS != 0 or h.second != 0:
        raise RegraNegocioError(
            f"Hora deve estar em intervalos de {INTERVALO_MINUTOS} minutos"
        )


def validar_nao_fim_de_semana(d: date) -> None:
    # weekday(): 0=segunda, 6=domingo
    if d.weekday() >= 5:
        raise RegraNegocioError("Não é possível agendar em fim de semana")


def validar_antecedencia(
    d: date, h: time, agora: Optional[datetime] = None
) -> None:
    agora = agora or datetime.now()
    alvo = datetime.combine(d, h)
    if alvo < agora:
        raise RegraNegocioError("Não é possível agendar no passado")
    if (alvo - agora) < timedelta(minutes=ANTECEDENCIA_MINIMA_MINUTOS):
        raise RegraNegocioError(
            f"Agendamento exige antecedência mínima de "
            f"{ANTECEDENCIA_MINIMA_MINUTOS} minutos"
        )


def validar_horario_medico(h: time, horario_medico: Optional[str]) -> None:
    """
    Confere se a hora está dentro do horário do médico.
    Formato esperado: "08:00-12:00" ou "08:00-12:00,14:00-18:00".
    Se vazio/None, considera o expediente geral.
    """
    if not horario_medico:
        return
    janelas = [j.strip() for j in horario_medico.split(",") if j.strip()]
    for janela in janelas:
        try:
            ini_s, fim_s = janela.split("-")
            ini = datetime.strptime(ini_s.strip(), "%H:%M").time()
            fim = datetime.strptime(fim_s.strip(), "%H:%M").time()
        except ValueError:
            raise RegraNegocioError(
                "Horário do médico mal formatado (use 'HH:MM-HH:MM')"
            )
        if ini <= h < fim:
            return
    raise RegraNegocioError(
        f"Hora {h.strftime('%H:%M')} fora do horário de atendimento do médico"
    )


# ── REGRA DE RETORNO ─────────────────────────

def validar_retorno_tem_consulta_previa(
    data_consulta_anterior: Optional[date],
    data_retorno: date,
) -> None:
    """
    Retorno só é permitido se houver consulta anterior do mesmo paciente
    com o mesmo médico dentro da janela de JANELA_RETORNO_DIAS.
    """
    if data_consulta_anterior is None:
        raise RegraNegocioError(
            "Retorno exige consulta anterior do paciente com este médico"
        )
    delta = (data_retorno - data_consulta_anterior).days
    if delta < 0 or delta > JANELA_RETORNO_DIAS:
        raise RegraNegocioError(
            f"Retorno só é válido em até {JANELA_RETORNO_DIAS} dias após a "
            f"última consulta"
        )


# ── CÁLCULOS ─────────────────────────────────

def calcular_preco(tipo: str) -> float:
    validar_tipo(tipo)
    return PRECO_DURACAO[tipo]["preco"]


def calcular_duracao_minutos(tipo: str) -> int:
    validar_tipo(tipo)
    return PRECO_DURACAO[tipo]["duracao_min"]


def calcular_fim(hora_inicio: time, tipo: str) -> time:
    duracao = calcular_duracao_minutos(tipo)
    base = datetime.combine(date.today(), hora_inicio)
    fim = base + timedelta(minutes=duracao)
    return fim.time()


def calcular_desconto_retorno(preco_base: float, eh_retorno: bool) -> float:
    """Retorno sempre tem 100% de desconto sobre o preço-base da consulta."""
    if eh_retorno:
        return preco_base
    return 0.0


# ── ORQUESTRADOR ─────────────────────────────

def validar_agendamento(
    data_str: str,
    hora_str: str,
    tipo: str,
    horario_medico: Optional[str] = None,
    email: Optional[str] = None,
    agora: Optional[datetime] = None,
) -> None:
    """
    Roda todas as validações de criação de consulta.
    Lança RegraNegocioError na primeira falha.
    """
    d = validar_formato_data(data_str)
    h = validar_formato_hora(hora_str)
    validar_tipo(tipo)
    validar_nao_fim_de_semana(d)
    validar_horario_comercial(h)
    validar_intervalo(h)
    validar_antecedencia(d, h, agora=agora)
    validar_horario_medico(h, horario_medico)
    if email:
        validar_email(email)
