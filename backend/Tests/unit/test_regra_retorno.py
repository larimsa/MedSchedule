# Foco em valores-limite da janela de JANELA_RETORNO_DIAS (30 dias)

import pytest
from datetime import date, timedelta

import services
from services import RegraNegocioError


pytestmark = pytest.mark.unit


class TestValidarRetornoTemConsultaPrevia:

    def test_sem_consulta_anterior_e_rejeitado(self):
        with pytest.raises(RegraNegocioError, match="consulta anterior"):
            services.validar_retorno_tem_consulta_previa(None, date(2026, 8, 10))

    def test_consulta_anterior_no_mesmo_dia_e_aceita(self):
        # borda inferior: delta == 0
        d = date(2026, 8, 10)
        services.validar_retorno_tem_consulta_previa(d, d)

    def test_consulta_anterior_dentro_da_janela_e_aceita(self):
        anterior = date(2026, 8, 1)
        retorno = date(2026, 8, 15)  # 14 dias depois
        services.validar_retorno_tem_consulta_previa(anterior, retorno)

    def test_consulta_anterior_exatamente_no_limite_de_30_dias_e_aceita(self):
        anterior = date(2026, 8, 1)
        retorno = anterior + timedelta(days=30)  # borda superior — incluída
        services.validar_retorno_tem_consulta_previa(anterior, retorno)

    def test_consulta_anterior_31_dias_antes_e_rejeitada(self):
        anterior = date(2026, 8, 1)
        retorno = anterior + timedelta(days=31)  # 1 dia além da borda
        with pytest.raises(RegraNegocioError, match="30 dias"):
            services.validar_retorno_tem_consulta_previa(anterior, retorno)

    def test_data_de_retorno_anterior_a_consulta_original_e_rejeitada(self):
        # delta negativo — a "consulta anterior" na verdade é depois do retorno
        anterior = date(2026, 8, 10)
        retorno = date(2026, 8, 5)
        with pytest.raises(RegraNegocioError):
            services.validar_retorno_tem_consulta_previa(anterior, retorno)
