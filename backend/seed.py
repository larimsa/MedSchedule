# ─────────────────────────────────────────────
# seed.py — Popula o banco com dados iniciais
# Execute uma vez: python seed.py
# ─────────────────────────────────────────────

from database import SessionLocal, engine
import models

# Cria as tabelas se não existirem
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Limpa dados anteriores
db.query(models.Consulta).delete()
db.query(models.Medico).delete()
db.commit()

# ── Médicos ──────────────────────────────────
medicos = [
    models.Medico(nome="Dr. Carlos Mendes",  crm="123456-SP", especialidade="Cardiologia",  email="carlos@medschedule.com",   telefone="(11) 99999-9999", endereco="Av. Paulista, 1000 — SP", horario="Seg–Sex, 08h–18h", cor=0),
    models.Medico(nome="Dra. Fernanda Lima",  crm="234567-SP", especialidade="Dermatologia", email="fernanda@medschedule.com",  telefone="(11) 98888-8888", endereco="Av. Paulista, 1000 — SP", horario="Seg–Sex, 09h–17h", cor=1),
    models.Medico(nome="Dr. Rafael Souza",    crm="345678-SP", especialidade="Pediatria",    email="rafael@medschedule.com",   telefone="(11) 97777-7777", endereco="Av. Paulista, 1000 — SP", horario="Seg–Sex, 08h–16h", cor=2),
    models.Medico(nome="Dra. Camila Torres",  crm="456789-SP", especialidade="Neurologia",   email="camila@medschedule.com",   telefone="(11) 96666-6666", endereco="Av. Paulista, 1000 — SP", horario="Ter–Sáb, 10h–18h", cor=3),
    models.Medico(nome="Dr. André Oliveira",  crm="567890-SP", especialidade="Ortopedia",    email="andre@medschedule.com",    telefone="(11) 95555-5555", endereco="Av. Paulista, 1000 — SP", horario="Seg–Sex, 07h–15h", cor=4),
    models.Medico(nome="Dra. Juliana Rocha",  crm="678901-SP", especialidade="Ginecologia",  email="juliana@medschedule.com",  telefone="(11) 94444-4444", endereco="Av. Paulista, 1000 — SP", horario="Seg–Sex, 08h–18h", cor=5),
]

db.add_all(medicos)
db.commit()

# Recarrega para pegar os IDs gerados
for m in medicos:
    db.refresh(m)

carlos, fernanda, rafael, camila, andre, juliana = medicos

# ── Consultas ────────────────────────────────
consultas = [
    # Dr. Carlos Mendes — Cardiologia
    models.Consulta(medico_id=carlos.id,   nome="João Silva",       email="joao@email.com",    telefone="(11) 91111-1111", data="2026-05-27", hora="09:00", tipo="consulta", observacoes=""),
    models.Consulta(medico_id=carlos.id,   nome="Maria Oliveira",   email="maria@email.com",   telefone="(11) 92222-2222", data="2026-05-27", hora="10:30", tipo="retorno",  observacoes="Resultado de exame pendente"),
    models.Consulta(medico_id=carlos.id,   nome="Pedro Santos",     email="pedro@email.com",   telefone="(11) 93333-3333", data="2026-05-27", hora="14:00", tipo="exame",    observacoes=""),
    models.Consulta(medico_id=carlos.id,   nome="Ana Lima",         email="ana@email.com",     telefone="(11) 94444-4444", data="2026-05-27", hora="15:30", tipo="consulta", observacoes="Primeira consulta"),
    models.Consulta(medico_id=carlos.id,   nome="Carlos Rocha",     email="cr@email.com",      telefone="(11) 95555-5555", data="2026-05-28", hora="09:00", tipo="retorno",  observacoes=""),
    models.Consulta(medico_id=carlos.id,   nome="Beatriz Costa",    email="bea@email.com",     telefone="(11) 96666-6666", data="2026-05-28", hora="11:00", tipo="consulta", observacoes=""),

    # Dra. Fernanda Lima — Dermatologia
    models.Consulta(medico_id=fernanda.id, nome="Isabela Neves",    email="isa@email.com",     telefone="(11) 91212-1212", data="2026-05-27", hora="09:30", tipo="consulta", observacoes="Mancha suspeita no braço"),
    models.Consulta(medico_id=fernanda.id, nome="Roberto Alves",    email="rob@email.com",     telefone="(11) 91313-1313", data="2026-05-27", hora="11:00", tipo="retorno",  observacoes=""),
    models.Consulta(medico_id=fernanda.id, nome="Thiago Campos",    email="thi@email.com",     telefone="(11) 91515-1515", data="2026-05-28", hora="10:00", tipo="exame",    observacoes="Biópsia de pele"),

    # Dr. Rafael Souza — Pediatria
    models.Consulta(medico_id=rafael.id,   nome="Sofia Mendes",     email="sofia@email.com",   telefone="(11) 91717-1717", data="2026-05-27", hora="08:30", tipo="consulta", observacoes="Febre persistente"),
    models.Consulta(medico_id=rafael.id,   nome="Miguel Azevedo",   email="mig@email.com",     telefone="(11) 91818-1818", data="2026-05-27", hora="10:00", tipo="retorno",  observacoes="Pós-vacinação"),
    models.Consulta(medico_id=rafael.id,   nome="Davi Carvalho",    email="davi@email.com",    telefone="(11) 92020-2020", data="2026-05-28", hora="09:00", tipo="exame",    observacoes="Hemograma"),

    # Dra. Camila Torres — Neurologia
    models.Consulta(medico_id=camila.id,   nome="Marcelo Pinto",    email="marc@email.com",    telefone="(11) 92222-2222", data="2026-05-27", hora="10:00", tipo="consulta", observacoes="Enxaqueca crônica"),
    models.Consulta(medico_id=camila.id,   nome="Renata Faria",     email="ren@email.com",     telefone="(11) 92323-2323", data="2026-05-27", hora="14:30", tipo="retorno",  observacoes=""),
    models.Consulta(medico_id=camila.id,   nome="Paulo Gonçalves",  email="pau@email.com",     telefone="(11) 92424-2424", data="2026-05-28", hora="10:30", tipo="exame",    observacoes="EEG agendado"),

    # Dr. André Oliveira — Ortopedia
    models.Consulta(medico_id=andre.id,    nome="Gustavo Leal",     email="gus@email.com",     telefone="(11) 92626-2626", data="2026-05-27", hora="08:00", tipo="consulta", observacoes="Dor no joelho"),
    models.Consulta(medico_id=andre.id,    nome="Fernanda Braga",   email="fern2@email.com",   telefone="(11) 92727-2727", data="2026-05-27", hora="11:30", tipo="retorno",  observacoes="Pós-operatório"),
    models.Consulta(medico_id=andre.id,    nome="Rodrigo Cunha",    email="rod@email.com",     telefone="(11) 92828-2828", data="2026-05-28", hora="09:30", tipo="exame",    observacoes="Raio-X coluna"),

    # Dra. Juliana Rocha — Ginecologia
    models.Consulta(medico_id=juliana.id,  nome="Vanessa Teixeira", email="van@email.com",     telefone="(11) 93030-3030", data="2026-05-27", hora="09:00", tipo="consulta", observacoes="Pré-natal"),
    models.Consulta(medico_id=juliana.id,  nome="Sandra Vieira",    email="san@email.com",     telefone="(11) 93131-3131", data="2026-05-27", hora="10:30", tipo="retorno",  observacoes="Resultado de ultrassom"),
    models.Consulta(medico_id=juliana.id,  nome="Mariana Luz",      email="mari@email.com",    telefone="(11) 93333-3333", data="2026-05-28", hora="09:30", tipo="exame",    observacoes="Papanicolau"),
]

db.add_all(consultas)
db.commit()
db.close()

print("✅ Banco populado com sucesso!")
print(f"   {len(medicos)} médicos | {len(consultas)} consultas")
