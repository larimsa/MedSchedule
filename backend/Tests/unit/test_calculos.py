# ─────────────────────────────────────────────
# tests/unit/test_calculos.py
#
# Testes de UNIDADE para as funções de cálculo (preço, duração, horário
# de fim e desconto de retorno). São funções puras e determinísticas:
# mesma entrada -> mesma saída, sem I/O — o alvo ideal para teste de
# unidade segundo a Aula 10 (pirâmide) e o "design guideline" do talk
# de Otavio Lemos (Comprehensible / Explicit I-O / Deterministic).
# ─────────────────────────────────────────────

import pytest
from datetime import time

import services
from services import RegraNegocioError


pytestmark = pytest.mark.unit


class TestCalcularPreco:

    @pytest.mark.parametrize("tipo, preco_esperado", [
        ("consulta", 200.0),
        ("retorno", 0.0),
        ("exame", 350.0),
    ])
    def test_preco_por_tipo(self, tipo, preco_esperado):
        assert services.calcular_preco(tipo) == preco_esperado

    def test_tipo_invalido_levanta_erro(self):
        with pytest.raises(RegraNegocioError):
            services.calcular_preco("cirurgia")


class TestCalcularDuracaoMinutos:

    @pytest.mark.parametrize("tipo, duracao_esperada", [
        ("consulta", 30),
        ("retorno", 15),
        ("exame", 45),
    ])
    def test_duracao_por_tipo(self, tipo, duracao_esperada):
        assert services.calcular_duracao_minutos(tipo) == duracao_esperada

    def test_tipo_invalido_levanta_erro(self):
        with pytest.raises(RegraNegocioError):
            services.calcular_duracao_minutos("cirurgia")


class TestCalcularFim:

    def test_fim_de_consulta_30min(self):
        assert services.calcular_fim(time(9, 0), "consulta") == time(9, 30)

    def test_fim_de_exame_45min(self):
        assert services.calcular_fim(time(9, 0), "exame") == time(9, 45)

    def test_fim_de_retorno_15min(self):
        assert services.calcular_fim(time(9, 0), "retorno") == time(9, 15)

    def test_fim_atravessando_a_hora_cheia(self):
        # 17:45 + 30min = 18:15 -> cobre a "virada" de hora
        assert services.calcular_fim(time(17, 45), "consulta") == time(18, 15)


class TestCalcularDescontoRetorno:

    def test_retorno_tem_desconto_total(self):
        assert services.calcular_desconto_retorno(200.0, eh_retorno=True) == 200.0

    def test_consulta_normal_nao_tem_desconto(self):
        assert services.calcular_desconto_retorno(200.0, eh_retorno=False) == 0.0

    def test_preco_base_zero_com_desconto(self):
        # valor de borda: preço-base zero
        assert services.calcular_desconto_retorno(0.0, eh_retorno=True) == 0.0
