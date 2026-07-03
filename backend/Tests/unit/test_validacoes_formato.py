import pytest
from datetime import date, time

import services
from services import RegraNegocioError


pytestmark = pytest.mark.unit


class TestValidarFormatoData:

    def test_data_valida_retorna_objeto_date(self):
        resultado = services.validar_formato_data("2026-08-10")
        assert resultado == date(2026, 8, 10)

    @pytest.mark.parametrize("entrada", [
        "",
        None,
        "10-08-2026",       # formato invertido (classe inválida: separador na ordem errada)
        "2026/08/10",       # separador errado
        "2026-8-10",        # sem zero à esquerda
        "26-08-10",         # ano com 2 dígitos
        "2026-08-10T00:00", # com hora junto
        "não é data",
    ])
    def test_formato_invalido_levanta_erro(self, entrada):
        with pytest.raises(RegraNegocioError):
            services.validar_formato_data(entrada)

    def test_data_inexistente_mas_com_formato_correto(self):
        # 30 de fevereiro não existe: passa na regex, falha no strptime
        with pytest.raises(RegraNegocioError):
            services.validar_formato_data("2026-02-30")

    def test_ano_bissexto_29_fevereiro_e_valido(self):
        # 2028 é bissexto - valor de borda válido para o mês de fevereiro
        assert services.validar_formato_data("2028-02-29") == date(2028, 2, 29)


class TestValidarFormatoHora:

    def test_hora_valida_retorna_objeto_time(self):
        assert services.validar_formato_hora("14:30") == time(14, 30)

    @pytest.mark.parametrize("entrada", [
        "00:00",   # borda inferior do domínio de tempo (válida como formato)
        "23:59",   # borda superior do domínio de tempo (válida como formato)
    ])
    def test_bordas_validas_do_dominio_de_tempo(self, entrada):
        # validar_formato_hora só checa o formato
        # regras de expediente ficam em validar_horario_comercial
        services.validar_formato_hora(entrada)  # não deve levantar

    @pytest.mark.parametrize("entrada", [
        "",
        None,
        "24:00",     # hora fora do domínio válido (0-23)
        "9:00",      # sem zero à esquerda
        "09:60",     # minuto fora do domínio válido (0-59)
        "09:00:00",  # com segundos
        "09h00",
    ])
    def test_formato_invalido_levanta_erro(self, entrada):
        with pytest.raises(RegraNegocioError):
            services.validar_formato_hora(entrada)


class TestValidarEmail:

    @pytest.mark.parametrize("email_valido", [
        "a@b.co",
        "paciente.teste@medschedule.com",
        "nome+tag@dominio.com.br",
    ])
    def test_emails_validos_nao_levantam_erro(self, email_valido):
        services.validar_email(email_valido)  # não deve levantar

    @pytest.mark.parametrize("email_invalido", [
        "",
        None,
        "sem-arroba.com",
        "@sem-usuario.com",
        "sem-dominio@",
        "com espaco@dominio.com",
        "sem-ponto@dominio",
    ])
    def test_emails_invalidos_levantam_erro(self, email_invalido):
        with pytest.raises(RegraNegocioError):
            services.validar_email(email_invalido)


class TestValidarCrm:

    @pytest.mark.parametrize("crm_valido", [
        "CRM/SP 123456",
        "CRM/RJ 1234",       # borda inferior de dígitos (4)
        "CRM/MG 123456",     # borda superior de dígitos (6)
        "123456-SP",
        "1234-RJ",
        "123456",
        "1234",
    ])
    def test_crms_validos_nao_levantam_erro(self, crm_valido):
        services.validar_crm(crm_valido)  # não deve levantar

    def test_crm_e_normalizado_para_maiusculo_antes_de_validar(self):
        services.validar_crm("crm/sp 123456")  # minúsculo também deve passar

    @pytest.mark.parametrize("crm_invalido", [
        "",
        None,
        "123",           # abaixo do mínimo de 4 dígitos
        "1234567",       # acima do máximo de 6 dígitos
        "CRM/S 123456",  # UF com 1 letra só
        "CRM/SPX 123456",# UF com 3 letras
        "SP-123456",     # ordem invertida do formato com traço
        "abcdef",        # letras onde deveriam ser dígitos
    ])
    def test_crms_invalidos_levantam_erro(self, crm_invalido):
        with pytest.raises(RegraNegocioError):
            services.validar_crm(crm_invalido)


class TestValidarTipo:

    @pytest.mark.parametrize("tipo", ["consulta", "retorno", "exame"])
    def test_tipos_validos_nao_levantam_erro(self, tipo):
        services.validar_tipo(tipo)

    @pytest.mark.parametrize("tipo", ["", None, "Consulta", "cirurgia", "retorno "])
    def test_tipos_invalidos_levantam_erro(self, tipo):
        with pytest.raises(RegraNegocioError):
            services.validar_tipo(tipo)
