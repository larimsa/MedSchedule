# ─────────────────────────────────────────────
# tests/integration/test_consultas_regras_com_banco.py
#
# Estas regras de negócio (conflito de horário, paciente duplicado,
# limite diário, retorno com histórico) vivem DENTRO do router
# (routers/consultas.py), não em services.py — porque dependem de
# consultar o estado atual do banco. Por isso NÃO podem ser testadas
# como unidade pura: são candidatas naturais a teste de integração
# (IO-dependent, conforme Ted Young / Aula 10).
# ─────────────────────────────────────────────

import pytest
from datetime import date, timedelta


pytestmark = pytest.mark.integration


def _proxima_segunda(a_partir_de: date) -> date:
    dias = (7 - a_partir_de.weekday()) % 7
    dias = dias if dias != 0 else 7
    return a_partir_de + timedelta(days=dias)


class TestConflitoDeHorario:

    def test_dois_agendamentos_mesmo_medico_mesma_data_hora_e_rejeitado(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"], "nome": "Paciente 1"}
        assert client.post("/consultas/", json=payload).status_code == 201

        payload_conflitante = {**payload, "nome": "Paciente 2"}
        resp = client.post("/consultas/", json=payload_conflitante)
        assert resp.status_code == 400
        assert "já está ocupado" in resp.json()["detail"]

    def test_mesmo_horario_com_medicos_diferentes_e_permitido(
        self, client, criar_medico, consulta_payload
    ):
        medico_a = criar_medico()
        medico_b = criar_medico(crm="444444-SP", email="c@medschedule.com")

        # nomes de pacientes diferentes: queremos isolar a regra de CONFLITO
        # DE HORÁRIO DO MÉDICO da regra de paciente-duplicado-no-mesmo-dia
        r1 = client.post(
            "/consultas/",
            json={**consulta_payload, "medico_id": medico_a["id"], "nome": "Paciente do Medico A"},
        )
        r2 = client.post(
            "/consultas/",
            json={**consulta_payload, "medico_id": medico_b["id"], "nome": "Paciente do Medico B"},
        )
        assert r1.status_code == 201
        assert r2.status_code == 201


class TestPacienteDuplicadoNoMesmoDia:

    def test_mesmo_paciente_duas_consultas_mesmo_dia_e_rejeitado(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"], "nome": "Paciente Repetido"}
        assert client.post("/consultas/", json=payload).status_code == 201

        payload_outro_horario = {**payload, "hora": "11:00"}  # mesmo dia, hora diferente
        resp = client.post("/consultas/", json=payload_outro_horario)
        assert resp.status_code == 400
        assert "já possui consulta agendada" in resp.json()["detail"]

    def test_mesmo_paciente_dias_diferentes_e_permitido(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {**consulta_payload, "medico_id": medico["id"], "nome": "Paciente Recorrente"}
        assert client.post("/consultas/", json=payload).status_code == 201

        data_original = date.fromisoformat(payload["data"])
        proximo_dia_util = _proxima_segunda(data_original)
        payload_outro_dia = {**payload, "data": proximo_dia_util.isoformat()}
        resp = client.post("/consultas/", json=payload_outro_dia)
        assert resp.status_code == 201


class TestLimiteDiarioPorMedico:

    def test_medico_atinge_limite_de_16_consultas_no_dia(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        # 08:00 até 17:30 em passos de 30min = 20 horários possíveis no dia;
        # criamos os 16 primeiros (limite) com pacientes diferentes.
        horarios = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in (0, 30)][:16]

        for i, hora in enumerate(horarios):
            payload = {
                **consulta_payload,
                "medico_id": medico["id"],
                "nome": f"Paciente {i}",
                "hora": hora,
            }
            resp = client.post("/consultas/", json=payload)
            assert resp.status_code == 201, f"falhou no horário {hora}: {resp.text}"

        # 17ª consulta do dia deve estourar o limite
        payload_extra = {
            **consulta_payload,
            "medico_id": medico["id"],
            "nome": "Paciente Extra",
            "hora": "17:30",
        }
        resp = client.post("/consultas/", json=payload_extra)
        assert resp.status_code == 400
        assert "limite" in resp.json()["detail"]


class TestRegraDeRetorno:

    def test_retorno_sem_consulta_anterior_e_rejeitado(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        payload = {
            **consulta_payload,
            "medico_id": medico["id"],
            "nome": "Paciente Sem Historico",
            "tipo": "retorno",
        }
        resp = client.post("/consultas/", json=payload)
        assert resp.status_code == 400
        assert "consulta anterior" in resp.json()["detail"]

    def test_retorno_com_consulta_anterior_dentro_da_janela_e_aceito(
        self, client, criar_medico, consulta_payload
    ):
        medico = criar_medico()
        nome_paciente = "Paciente Com Historico"

        data_consulta = date.fromisoformat(consulta_payload["data"])
        payload_consulta = {
            **consulta_payload,
            "medico_id": medico["id"],
            "nome": nome_paciente,
            "tipo": "consulta",
        }
        assert client.post("/consultas/", json=payload_consulta).status_code == 201

        # segunda seguinte (7 dias depois) -> mesma janela de expediente,
        # dentro dos 30 dias de retorno
        data_retorno = data_consulta + timedelta(days=7)
        payload_retorno = {
            **consulta_payload,
            "medico_id": medico["id"],
            "nome": nome_paciente,
            "tipo": "retorno",
            "data": data_retorno.isoformat(),
            "hora": "11:00",  # horário diferente p/ não bater no limite de paciente/dia
        }
        resp = client.post("/consultas/", json=payload_retorno)
        assert resp.status_code == 201

    def test_retorno_com_medico_diferente_da_consulta_original_e_rejeitado(
        self, client, criar_medico, consulta_payload
    ):
        medico_a = criar_medico()
        medico_b = criar_medico(crm="555555-SP", email="d@medschedule.com")
        nome_paciente = "Paciente Trocou De Medico"

        data_consulta = date.fromisoformat(consulta_payload["data"])
        payload_consulta = {
            **consulta_payload,
            "medico_id": medico_a["id"],
            "nome": nome_paciente,
            "tipo": "consulta",
        }
        assert client.post("/consultas/", json=payload_consulta).status_code == 201

        data_retorno = data_consulta + timedelta(days=7)
        payload_retorno = {
            **consulta_payload,
            "medico_id": medico_b["id"],  # médico diferente!
            "nome": nome_paciente,
            "tipo": "retorno",
            "data": data_retorno.isoformat(),
        }
        resp = client.post("/consultas/", json=payload_retorno)
        assert resp.status_code == 400
        assert "consulta anterior" in resp.json()["detail"]
