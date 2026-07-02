import sys
import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models  
from database import Base, get_db 
from main import app  




@pytest.fixture()
def db_engine():
    """
    Um banco SQLite em memória novo para cada teste que precisar de IO real.
    StaticPool garante que a mesma conexão (logo o mesmo :memory:) seja
    reaproveitada entre as sessões abertas durante o teste.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Sessão de banco isolada, para testes de integração que falam direto com o SQLAlchemy."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine):
    """
    TestClient da API com o get_db substituído por um banco SQLite de teste.
    Usado pelos testes de INTEGRAÇÃO (endpoint + banco real) e E2E (fluxo completo).
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── HELPERS DE DOMÍNIO ─────────────────────────────────────────

@pytest.fixture()
def medico_payload():
    """Payload mínimo válido para criar um médico via API."""
    return {
        "nome": "Dr. Teste Santos",
        "crm": "111111-SP",
        "especialidade": "Clínica Geral",
        "email": "teste@medschedule.com",
        "telefone": "(11) 90000-0000",
        "endereco": "Rua Teste, 1",
        "horario": "Seg–Sex, 08h–18h",
        "cor": 0,
    }


@pytest.fixture()
def criar_medico(client, medico_payload):
    """Cria um médico via API e devolve o objeto já persistido (dict)."""
    def _criar(**overrides):
        payload = {**medico_payload, **overrides}
        resp = client.post("/medicos/", json=payload)
        assert resp.status_code == 201, resp.text
        return resp.json()
    return _criar


def data_futura_valida():
    """
    Retorna (data_str, hora_str) para uma próxima segunda-feira útil
    às 10:00, sempre no futuro (>60min de antecedência), evitando
    dependência de "hoje" nos testes.
    """
    from datetime import date, timedelta

    hoje = date.today()
    dias_ate_segunda = (7 - hoje.weekday()) % 7
    dias_ate_segunda = dias_ate_segunda if dias_ate_segunda != 0 else 7
    proxima_segunda = hoje + timedelta(days=dias_ate_segunda + 7)  # +7 p/ margem de sobra
    return proxima_segunda.isoformat(), "10:00"


@pytest.fixture()
def consulta_payload():
    data_str, hora_str = data_futura_valida()
    return {
        "medico_id": None,  # preenchido no teste
        "nome": "Paciente Teste",
        "email": "paciente@email.com",
        "telefone": "(11) 91234-5678",
        "data": data_str,
        "hora": hora_str,
        "tipo": "consulta",
        "observacoes": "",
    }
