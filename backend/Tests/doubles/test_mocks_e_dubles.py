import pytest
from datetime import datetime
from unittest.mock import MagicMock

import services


pytestmark = pytest.mark.mock


class TestValidarAntecedenciaComStubDeRelogio:
    """
    Stub: substituímos datetime.now() por um valor fixo para não
    depender do relógio real da máquina — sem isso, o teste seria
    "flaky" perto da virada de minuto/dia.
    """

    def test_validar_antecedencia_usa_relogio_congelado(self, monkeypatch):
        agora_fixo = datetime(2026, 8, 3, 10, 0)

        class RelogioFixo(datetime):
            @classmethod
            def now(cls, tz=None):
                return agora_fixo

        monkeypatch.setattr(services, "datetime", RelogioFixo)

        # 10:30 está a 30min de "agora" -> deve falhar por antecedência insuficiente
        with pytest.raises(services.RegraNegocioError):
            services.validar_antecedencia(agora_fixo.date(), agora_fixo.time().replace(minute=30))

        # 11:30 está a 90min de "agora" -> deve passar
        services.validar_antecedencia(agora_fixo.date(), agora_fixo.time().replace(hour=11, minute=30))


class TestRouterConsultasComSessionMockada:
    """
    Testa a lógica de routers/consultas.py isolando a Session do
    SQLAlchemy com um Mock Object — não sobe nenhum banco real.
    
    """

    def test_buscar_medico_inexistente_levanta_http_404_com_session_mockada(self):
        from fastapi import HTTPException
        from routers import medicos as medicos_router

        session_mock = MagicMock()
        # Simula: query(...).filter(...).first() -> None (médico não existe)
        session_mock.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            medicos_router.buscar_medico(medico_id=9999, db=session_mock)

        assert exc_info.value.status_code == 404
        session_mock.query.assert_called_once()

    def test_criar_consulta_para_medico_inexistente_nao_chega_a_commitar(self):

        from fastapi import HTTPException
        from routers import consultas as consultas_router
        import schemas

        session_mock = MagicMock()
        session_mock.query.return_value.filter.return_value.first.return_value = None  # médico não existe

        dados = schemas.ConsultaCreate(
            medico_id=9999,
            nome="Paciente Mock",
            email="mock@email.com",
            telefone="",
            data="2026-08-03",
            hora="10:00",
            tipo="consulta",
            observacoes="",
        )

        with pytest.raises(HTTPException) as exc_info:
            consultas_router.criar_consulta(dados=dados, db=session_mock)

        assert exc_info.value.status_code == 404
        session_mock.add.assert_not_called()
        session_mock.commit.assert_not_called()
