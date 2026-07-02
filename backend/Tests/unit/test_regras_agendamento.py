import pytest
from datetime import date, time, datetime, timedelta

import services
from services import RegraNegocioError


pytestmark = pytest.mark.unit


# validar_horario_comercial (borda: 08:00 e 18:00)

class TestHorarioComercial:

    @pytest.mark.parametrize("hora", [
        time(8, 0),    
        time(8, 1),
        time(12, 0),
        time(17, 59),  
    ])
    def test_horarios_dentro_do_expediente_sao_aceitos(self, hora):
        services.validar_horario_comercial(hora)  # não deve levantar

    @pytest.mark.parametrize("hora", [
        time(7, 59),  
        time(0, 0),
        time(18, 0),   
        time(18, 1),
        time(23, 59),
    ])
    def test_horarios_fora_do_expediente_sao_rejeitados(self, hora):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_comercial(hora)


# (múltiplos de 30 minutos)

class TestValidarIntervalo:

    @pytest.mark.parametrize("hora", [
        time(9, 0),
        time(9, 30),
        time(14, 0),
    ])
    def test_minutos_multiplos_de_30_sao_aceitos(self, hora):
        services.validar_intervalo(hora)  # não deve levantar

    @pytest.mark.parametrize("hora", [
        time(9, 1),
        time(9, 15),
        time(9, 29),   
        time(9, 31),   
        time(9, 59),
    ])
    def test_minutos_fora_do_intervalo_sao_rejeitados(self, hora):
        with pytest.raises(RegraNegocioError):
            services.validar_intervalo(hora)


class TestNaoFimDeSemana:

    @pytest.mark.parametrize("dia_semana_iso", range(0, 5))  # segunda..sexta
    def test_dias_uteis_sao_aceitos(self, dia_semana_iso):
        # 2026-08-03 é uma segunda-feira; soma dias p/ cobrir seg..sex
        segunda = date(2026, 8, 3)
        d = segunda + timedelta(days=dia_semana_iso)
        services.validar_nao_fim_de_semana(d)  # não deve levantar

    @pytest.mark.parametrize("dia_semana_iso", [5, 6])  # sábado, domingo
    def test_fim_de_semana_e_rejeitado(self, dia_semana_iso):
        segunda = date(2026, 8, 3)
        d = segunda + timedelta(days=dia_semana_iso)
        with pytest.raises(RegraNegocioError):
            services.validar_nao_fim_de_semana(d)


class TestValidarAntecedencia:

    def test_agendamento_no_passado_e_rejeitado(self):
        agora = datetime(2026, 8, 3, 10, 0)
        with pytest.raises(RegraNegocioError, match="passado"):
            services.validar_antecedencia(date(2026, 8, 3), time(9, 0), agora=agora)

    def test_antecedencia_menor_que_minima_e_rejeitada(self):
        agora = datetime(2026, 8, 3, 10, 0)
        # alvo às 10:30 -> soh 30min de antecedência (< 60 exigidos)
        with pytest.raises(RegraNegocioError, match="antecedência"):
            services.validar_antecedencia(date(2026, 8, 3), time(10, 30), agora=agora)

    def test_antecedencia_exatamente_no_limite_e_aceita(self):
        # valor de borda: exatamente 60 minutos deve ser aceito (delta < 60 que falha, == 60 passa)
        agora = datetime(2026, 8, 3, 10, 0)
        services.validar_antecedencia(date(2026, 8, 3), time(11, 0), agora=agora)

    def test_antecedencia_um_minuto_abaixo_do_limite_e_rejeitada(self):
        agora = datetime(2026, 8, 3, 10, 0)
        with pytest.raises(RegraNegocioError):
            services.validar_antecedencia(date(2026, 8, 3), time(10, 59), agora=agora)

    def test_antecedencia_um_minuto_acima_do_limite_e_aceita(self):
        agora = datetime(2026, 8, 3, 10, 0)
        services.validar_antecedencia(date(2026, 8, 3), time(11, 1), agora=agora)

    def test_usa_datetime_now_quando_agora_nao_e_informado(self):
        # cobre o branch "agora = agora or datetime.now()"
        futuro = datetime.now() + timedelta(days=1)
        services.validar_antecedencia(futuro.date(), futuro.time().replace(second=0, microsecond=0))

    def test_alvo_exatamente_igual_a_agora_nao_e_tratado_como_passado(self):
        # Teste de mutação: mata o mutante que troca "alvo < agora" por
        # "alvo <= agora". Se alvo == agora, a mensagem esperada é a de
        # ANTECEDÊNCIA insuficiente (0min < 60min exigidos) — e não a de
        # "agendar no passado". Um mutante <= confundiria os dois casos.
        agora = datetime(2026, 8, 3, 10, 0)
        with pytest.raises(RegraNegocioError, match="antecedência") as excinfo:
            services.validar_antecedencia(date(2026, 8, 3), time(10, 0), agora=agora)
        assert "passado" not in str(excinfo.value)


# (múltiplas janelas / cobertura de decisões) ──

class TestValidarHorarioMedico:

    def test_sem_horario_cadastrado_aceita_qualquer_hora(self):
        # branch: "if not horario_medico: return"
        services.validar_horario_medico(time(23, 0), None)
        services.validar_horario_medico(time(23, 0), "")

    def test_hora_dentro_da_unica_janela_e_aceita(self):
        services.validar_horario_medico(time(9, 0), "08:00-12:00")

    def test_hora_fora_da_unica_janela_e_rejeitada(self):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_medico(time(13, 0), "08:00-12:00")

    def test_hora_na_borda_inicial_da_janela_e_aceita(self):
        services.validar_horario_medico(time(8, 0), "08:00-12:00")

    def test_hora_na_borda_final_da_janela_e_rejeitada(self):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_medico(time(12, 0), "08:00-12:00")

    def test_hora_na_segunda_janela_de_duas_e_aceita(self):
        services.validar_horario_medico(time(15, 0), "08:00-12:00,14:00-18:00")

    def test_hora_no_intervalo_entre_duas_janelas_e_rejeitada(self):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_medico(time(13, 0), "08:00-12:00,14:00-18:00")

    def test_horario_em_formato_livre_e_ignorado_silenciosamente(self):
        services.validar_horario_medico(time(23, 0), "Seg–Sex, 08h–18h")

    def test_horario_com_hifen_mas_hora_invalida_e_ignorado_via_valueerror(self):
        services.validar_horario_medico(time(23, 0), "manha-tarde")

    def test_janela_sem_hifen_e_ignorada_no_parsing(self):
        services.validar_horario_medico(time(9, 0), "08:00-12:00,horario livre")

    def test_mutacao_or_para_and_e_detectada_com_hora_fora_da_janela_valida(self):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_medico(time(15, 0), "08:00-12:00,sem hifen aqui")

    def test_mutacao_continue_para_break_e_detectada_com_janela_valida_apos_invalida(self):
        with pytest.raises(RegraNegocioError):
            services.validar_horario_medico(time(15, 0), "sem hifen aqui,08:00-12:00")
