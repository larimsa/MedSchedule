# ─────────────────────────────────────────────
# tests/unit/test_orquestrador.py
#
# validar_agendamento() encadeia todas as regras de negócio "puras".
# Mesmo sendo uma função "guarda-chuva", continua sendo teste de
# UNIDADE: nenhuma chamada toca banco, rede ou disco (IO-Free).
#
# Teste funcional (Aula 2): validamos o comportamento observável
# (levanta ou não RegraNegocioError, e com qual mensagem) e não a
# implementação interna de cada sub-regra.
# ─────────────────────────────────────────────

import pytest
from datetime import datetime

import services
from services import RegraNegocioError


pytestmark = pytest.mark.unit


AGORA_FIXO = datetime(2026, 8, 3, 8, 0)  # segunda-feira, 08:00


class TestValidarAgendamentoCaminhoFeliz:

    def test_agendamento_valido_nao_levanta_erro(self):
        services.validar_agendamento(
            data_str="2026-08-03",
            hora_str="10:00",
            tipo="consulta",
            horario_medico="08:00-12:00",
            email="paciente@email.com",
            agora=AGORA_FIXO,
        )

    def test_agendamento_valido_sem_email_e_sem_horario_medico(self):
        # email e horario_medico são opcionais
        services.validar_agendamento(
            data_str="2026-08-03",
            hora_str="10:00",
            tipo="exame",
            horario_medico=None,
            email=None,
            agora=AGORA_FIXO,
        )


class TestValidarAgendamentoCadaRegraBarraOAgendamento:
    """
    Cada teste aqui isola UMA violação por vez, mantendo as demais
    entradas válidas — assim, se o teste falhar, sabemos exatamente
    qual regra parou de barrar o agendamento (rastreabilidade).
    """

    def test_data_mal_formatada(self):
        with pytest.raises(RegraNegocioError, match="Data"):
            services.validar_agendamento("03/08/2026", "10:00", "consulta", agora=AGORA_FIXO)

    def test_hora_mal_formatada(self):
        with pytest.raises(RegraNegocioError, match="Hora"):
            services.validar_agendamento("2026-08-03", "10h00", "consulta", agora=AGORA_FIXO)

    def test_tipo_invalido(self):
        with pytest.raises(RegraNegocioError, match="Tipo inválido"):
            services.validar_agendamento("2026-08-03", "10:00", "cirurgia", agora=AGORA_FIXO)

    def test_fim_de_semana(self):
        # 2026-08-08 é sábado
        with pytest.raises(RegraNegocioError, match="fim de semana"):
            services.validar_agendamento("2026-08-08", "10:00", "consulta", agora=AGORA_FIXO)

    def test_fora_do_expediente(self):
        with pytest.raises(RegraNegocioError, match="expediente"):
            services.validar_agendamento("2026-08-03", "19:00", "consulta", agora=AGORA_FIXO)

    def test_fora_do_intervalo_de_30_minutos(self):
        with pytest.raises(RegraNegocioError, match="intervalos"):
            services.validar_agendamento("2026-08-03", "10:15", "consulta", agora=AGORA_FIXO)

    def test_antecedencia_insuficiente(self):
        with pytest.raises(RegraNegocioError, match="antecedência"):
            services.validar_agendamento("2026-08-03", "08:30", "consulta", agora=AGORA_FIXO)

    def test_fora_do_horario_do_medico(self):
        with pytest.raises(RegraNegocioError, match="horário de atendimento"):
            services.validar_agendamento(
                "2026-08-03", "14:00", "consulta",
                horario_medico="08:00-12:00", agora=AGORA_FIXO,
            )

    def test_email_invalido(self):
        with pytest.raises(RegraNegocioError, match="Email"):
            services.validar_agendamento(
                "2026-08-03", "10:00", "consulta",
                email="email-invalido", agora=AGORA_FIXO,
            )


class TestValidarAgendamentoOrdemDasValidacoes:
    """
    services.validar_agendamento roda as sub-regras em sequência e
    para na primeira falha. Este teste documenta a ordem esperada
    (formato antes de regra de negócio), que é uma decisão de design
    relevante para quem for adicionar uma nova validação no futuro.
    """

    def test_formato_de_data_e_checado_antes_do_tipo(self):
        # data inválida E tipo inválido ao mesmo tempo -> deve reclamar da data primeiro
        with pytest.raises(RegraNegocioError, match="Data"):
            services.validar_agendamento("data-invalida", "10:00", "cirurgia", agora=AGORA_FIXO)
