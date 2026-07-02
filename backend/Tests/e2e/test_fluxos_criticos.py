import pytest
from datetime import date, timedelta


pytestmark = pytest.mark.e2e


class TestFluxoCriticoDeAgendamento:
    """
    Caminho crítico nº 1: cadastrar médico -> agendar consulta ->
    consultar a cobrança -> paciente volta para retorno -> cancela.
    Isso cobre a jornada completa que a clínica mais usa no dia a dia.
    """

    def test_jornada_completa_cadastro_agendamento_retorno_e_cancelamento(self, client):
        # 1) Cadastra um médico
        resp_medico = client.post("/medicos/", json={
            "nome": "Dra. Helena Prado",
            "crm": "999999-SP",
            "especialidade": "Clínica Geral",
            "email": "helena@medschedule.com",
            "telefone": "(11) 90000-1111",
            "endereco": "Rua das Clínicas, 500",
            "horario": "Seg–Sex, 08h–18h",
            "cor": 1,
        })
        assert resp_medico.status_code == 201
        medico_id = resp_medico.json()["id"]

        # 2) Paciente agenda uma consulta (próxima segunda-feira útil)
        hoje = date.today()
        dias_ate_segunda = (7 - hoje.weekday()) % 7 or 7
        data_consulta = hoje + timedelta(days=dias_ate_segunda + 7)

        resp_consulta = client.post("/consultas/", json={
            "medico_id": medico_id,
            "nome": "Paciente Jornada Completa",
            "email": "paciente.jornada@email.com",
            "telefone": "(11) 98765-4321",
            "data": data_consulta.isoformat(),
            "hora": "09:00",
            "tipo": "consulta",
            "observacoes": "Primeira consulta",
        })
        assert resp_consulta.status_code == 201
        consulta_id = resp_consulta.json()["id"]

        # 3) A recepção consulta o valor a cobrar
        resp_cobranca = client.get(f"/consultas/{consulta_id}/cobranca")
        assert resp_cobranca.status_code == 200
        assert resp_cobranca.json()["preco"] == 200.0

        # 4) Uma semana depois, o mesmo paciente volta para retorno
        data_retorno = data_consulta + timedelta(days=7)
        resp_retorno = client.post("/consultas/", json={
            "medico_id": medico_id,
            "nome": "Paciente Jornada Completa",
            "email": "paciente.jornada@email.com",
            "telefone": "(11) 98765-4321",
            "data": data_retorno.isoformat(),
            "hora": "09:00",
            "tipo": "retorno",
            "observacoes": "",
        })
        assert resp_retorno.status_code == 201
        retorno_id = resp_retorno.json()["id"]

        # retorno é gratuito
        resp_cobranca_retorno = client.get(f"/consultas/{retorno_id}/cobranca")
        assert resp_cobranca_retorno.json()["preco"] == 0.0

        # 5) Paciente cancela a consulta original
        resp_cancelamento = client.delete(f"/consultas/{consulta_id}")
        assert resp_cancelamento.status_code == 204
        assert client.get(f"/consultas/{consulta_id}").status_code == 404

        # o retorno continua existindo (não foi afetado pelo cancelamento)
        assert client.get(f"/consultas/{retorno_id}").status_code == 200


class TestFluxoCriticoDeSaudeDaApi:
    """
    Caminho crítico nº 2: a API precisa estar viva e respondendo —
    é o primeiro checkpoint de qualquer verificação de deploy/monitoramento.
    """

    def test_api_sobe_e_responde_health_check(self, client):
        assert client.get("/").status_code == 200
        assert client.get("/health").json() == {"status": "ok"}
