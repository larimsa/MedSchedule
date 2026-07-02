import pytest


pytestmark = pytest.mark.integration


class TestCriarConsulta:

    def test_criar_consulta_valida_retorna_201(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"]}

        resp = client.post("/consultas/", json=payload)
        assert resp.status_code == 201
        corpo = resp.json()
        assert corpo["medico_id"] == medico["id"]
        assert corpo["tipo"] == "consulta"

    def test_criar_consulta_para_medico_inexistente_retorna_404(self, client, consulta_payload):
        payload = {**consulta_payload, "medico_id": 9999}
        resp = client.post("/consultas/", json=payload)
        assert resp.status_code == 404
        assert "Médico não encontrado" in resp.json()["detail"]

    def test_criar_consulta_com_regra_de_negocio_violada_retorna_400(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        # domingo -> viola validar_nao_fim_de_semana (regra pura, mas
        # o teste aqui confirma que o router de fato delega para services
        # e converte RegraNegocioError em HTTP 400)
        payload = {**consulta_payload, "medico_id": medico["id"], "data": "2026-08-09"}
        resp = client.post("/consultas/", json=payload)
        assert resp.status_code == 400


class TestListarEBuscarConsulta:

    def test_listar_consultas_filtrando_por_medico(self, client, criar_medico, consulta_payload):
        medico_a = criar_medico()
        medico_b = criar_medico(crm="333333-SP", email="b@medschedule.com")

        client.post("/consultas/", json={**consulta_payload, "medico_id": medico_a["id"], "nome": "Paciente A"})
        client.post("/consultas/", json={**consulta_payload, "medico_id": medico_b["id"], "nome": "Paciente B"})

        resp = client.get(f"/consultas/?medico_id={medico_a['id']}")
        assert resp.status_code == 200
        resultado = resp.json()
        assert len(resultado) == 1
        assert resultado[0]["nome"] == "Paciente A"

    def test_buscar_consulta_inexistente_retorna_404(self, client):
        resp = client.get("/consultas/9999")
        assert resp.status_code == 404

    def test_listar_consultas_filtrando_por_data(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        client.post("/consultas/", json={**consulta_payload, "medico_id": medico["id"]})

        resp = client.get(f"/consultas/?data={consulta_payload['data']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_listar_consultas_filtrando_por_tipo(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        client.post("/consultas/", json={**consulta_payload, "medico_id": medico["id"], "tipo": "exame"})

        resp_exame = client.get("/consultas/?tipo=exame")
        resp_retorno = client.get("/consultas/?tipo=retorno")
        assert len(resp_exame.json()) == 1
        assert len(resp_retorno.json()) == 0


class TestCobrancaConsulta:

    def test_cobranca_de_consulta_normal(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"], "tipo": "consulta"}
        consulta = client.post("/consultas/", json=payload).json()

        resp = client.get(f"/consultas/{consulta['id']}/cobranca")
        assert resp.status_code == 200
        corpo = resp.json()
        assert corpo["preco"] == 200.0
        assert corpo["duracao_minutos"] == 30
        assert corpo["hora_fim"] == "10:30"  # payload usa hora "10:00"

    def test_cobranca_de_exame_tem_preco_e_duracao_diferentes(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"], "tipo": "exame"}
        consulta = client.post("/consultas/", json=payload).json()

        resp = client.get(f"/consultas/{consulta['id']}/cobranca")
        assert resp.json()["preco"] == 350.0

    def test_cobranca_de_consulta_inexistente_retorna_404(self, client):
        resp = client.get("/consultas/9999/cobranca")
        assert resp.status_code == 404


class TestAtualizarConsulta:

    def test_atualizar_observacoes_nao_revalida_regras(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"]}
        consulta = client.post("/consultas/", json=payload).json()

        resp = client.put(f"/consultas/{consulta['id']}", json={"observacoes": "Trazer exames anteriores"})
        assert resp.status_code == 200
        assert resp.json()["observacoes"] == "Trazer exames anteriores"

    def test_atualizar_para_horario_invalido_retorna_400(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"]}
        consulta = client.post("/consultas/", json=payload).json()

        resp = client.put(f"/consultas/{consulta['id']}", json={"hora": "19:00"})
        assert resp.status_code == 400

    def test_atualizar_consulta_inexistente_retorna_404(self, client):
        resp = client.put("/consultas/9999", json={"observacoes": "x"})
        assert resp.status_code == 404

    def test_atualizar_hora_para_horario_ja_ocupado_por_outra_consulta_retorna_400(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload_base = {**consulta_payload, "medico_id": medico["id"]}

        # consulta A às 10:00 (payload padrão)
        consulta_a = client.post("/consultas/", json={**payload_base, "nome": "Paciente A"}).json()
        # consulta B às 11:00 (mesmo dia, médico e horário diferentes)
        consulta_b = client.post(
            "/consultas/", json={**payload_base, "nome": "Paciente B", "hora": "11:00"}
        ).json()

        # tenta mover a consulta B para o horário já ocupado pela consulta A
        resp = client.put(f"/consultas/{consulta_b['id']}", json={"hora": consulta_a["hora"]})
        assert resp.status_code == 400
        assert "já está ocupado" in resp.json()["detail"]


class TestDeletarConsulta:

    def test_deletar_consulta_existente_retorna_204(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"]}
        consulta = client.post("/consultas/", json=payload).json()

        resp = client.delete(f"/consultas/{consulta['id']}")
        assert resp.status_code == 204
        assert client.get(f"/consultas/{consulta['id']}").status_code == 404

    def test_deletar_consulta_inexistente_retorna_404(self, client):
        resp = client.delete("/consultas/9999")
        assert resp.status_code == 404
