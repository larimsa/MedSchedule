import pytest


pytestmark = pytest.mark.integration


class TestCriarMedico:

    def test_criar_medico_com_dados_validos_retorna_201(self, client, medico_payload):
        resp = client.post("/medicos/", json=medico_payload)
        assert resp.status_code == 201
        corpo = resp.json()
        assert corpo["nome"] == medico_payload["nome"]
        assert corpo["crm"] == medico_payload["crm"]
        assert "id" in corpo

    def test_criar_medico_persiste_no_banco(self, client, medico_payload):
        resp = client.post("/medicos/", json=medico_payload)
        medico_id = resp.json()["id"]

        busca = client.get(f"/medicos/{medico_id}")
        assert busca.status_code == 200
        assert busca.json()["crm"] == medico_payload["crm"]

    def test_crm_duplicado_retorna_400(self, client, medico_payload):
        client.post("/medicos/", json=medico_payload)
        resp = client.post("/medicos/", json=medico_payload)  # mesmo CRM de novo
        assert resp.status_code == 400
        assert "CRM já cadastrado" in resp.json()["detail"]

    def test_crm_invalido_retorna_400_antes_de_tocar_o_banco(self, client, medico_payload):
        payload = {**medico_payload, "crm": "abc"}
        resp = client.post("/medicos/", json=payload)
        assert resp.status_code == 400

    def test_email_invalido_retorna_400(self, client, medico_payload):
        payload = {**medico_payload, "email": "invalido"}
        resp = client.post("/medicos/", json=payload)
        assert resp.status_code == 400


class TestListarEBuscarMedico:

    def test_listar_medicos_vazio(self, client):
        resp = client.get("/medicos/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_medicos_apos_criacao(self, client, criar_medico):
        criar_medico()
        criar_medico(crm="222222-SP", email="outro@medschedule.com")

        resp = client.get("/medicos/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_buscar_medico_inexistente_retorna_404(self, client):
        resp = client.get("/medicos/9999")
        assert resp.status_code == 404


class TestAtualizarMedico:

    def test_atualizar_nome_do_medico(self, client, criar_medico):
        medico = criar_medico()
        resp = client.put(f"/medicos/{medico['id']}", json={"nome": "Dr. Novo Nome"})
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Dr. Novo Nome"

    def test_atualizar_medico_inexistente_retorna_404(self, client):
        resp = client.put("/medicos/9999", json={"nome": "Fulano"})
        assert resp.status_code == 404

    def test_atualizar_com_crm_invalido_retorna_400(self, client, criar_medico):
        medico = criar_medico()
        resp = client.put(f"/medicos/{medico['id']}", json={"crm": "x"})
        assert resp.status_code == 400

    def test_atualizar_com_email_invalido_retorna_400(self, client, criar_medico):
        medico = criar_medico()
        resp = client.put(f"/medicos/{medico['id']}", json={"email": "invalido"})
        assert resp.status_code == 400


class TestDeletarMedico:

    def test_deletar_medico_existente_retorna_204(self, client, criar_medico):
        medico = criar_medico()
        resp = client.delete(f"/medicos/{medico['id']}")
        assert resp.status_code == 204

        busca = client.get(f"/medicos/{medico['id']}")
        assert busca.status_code == 404

    def test_deletar_medico_inexistente_retorna_404(self, client):
        resp = client.delete("/medicos/9999")
        assert resp.status_code == 404

    def test_deletar_medico_remove_consultas_em_cascata(self, client, criar_medico, consulta_payload):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"]}
        consulta = client.post("/consultas/", json=payload).json()

        client.delete(f"/medicos/{medico['id']}")

        busca_consulta = client.get(f"/consultas/{consulta['id']}")
        assert busca_consulta.status_code == 404
