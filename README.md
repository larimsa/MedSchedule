# MedSchedule

Sistema de agendamento médico desenvolvido como trabalho final da disciplina de Validação e Verificação de Software.

A aplicação simula a rotina de uma clínica: cadastro de médicos, agendamento de consultas (consulta, retorno e exame), gestão da agenda diária e acompanhamento do histórico de atendimentos.

## Stack

- **Backend:** Python + FastAPI + SQLAlchemy
- **Banco:** PostgreSQL (hospedado no Supabase) — com fallback para SQLite local
- **Frontend:** HTML, CSS e JavaScript puro (sem framework)
- **Deploy:** Render (backend)

## Estrutura do projeto

```
MedSchedule/
├── backend/
│   ├── main.py            # entrada da API
│   ├── database.py        # conexão com o banco
│   ├── models.py          # tabelas (Medico, Consulta)
│   ├── schemas.py         # validação de entrada/saída (Pydantic)
│   ├── services.py        # regras de negócio
│   ├── seed.py            # popula o banco com dados iniciais
│   ├── routers/
│   │   ├── medicos.py
│   │   └── consultas.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── css/
    └── js/
```

## Banco de dados

Duas tabelas:

- **medicos** — `id`, `nome`, `crm` (único), `especialidade`, `email`, `telefone`, `endereco`, `horario`, `cor`, `created_at`, `updated_at`
- **consultas** — `id`, `medico_id` (FK), `nome` do paciente, `email`, `telefone`, `data`, `hora`, `tipo`, `observacoes`, `created_at`, `updated_at`

Restrições aplicadas no banco:
- CRM único em médicos
- Cascade delete: ao remover um médico, suas consultas são removidas
- Check constraint: `tipo` só aceita `consulta`, `retorno` ou `exame`
- Timestamps `created_at` e `updated_at` em ambas as tabelas (atualizam automaticamente)

## Regras de negócio

As validações ficam em `backend/services.py` e são acionadas pelos endpoints antes de qualquer escrita no banco:

- Formato obrigatório: data `YYYY-MM-DD`, hora `HH:MM`
- Hora dentro do expediente da clínica (08:00–18:00)
- Hora dentro do horário de atendimento do médico (campo `horario`)
- Intervalos de 30 minutos
- Não é permitido agendar em fim de semana
- Antecedência mínima de 60 minutos
- Conflito de horário: um médico não pode ter duas consultas no mesmo dia e hora
- Paciente não pode ter duas consultas no mesmo dia
- Limite diário por médico (16 consultas)
- Retorno só é permitido se houver consulta anterior do mesmo paciente com o mesmo médico nos últimos 30 dias
- Tipo de consulta restrito a `consulta`, `retorno` ou `exame`
- Validação de formato de CRM e e-mail no cadastro de médico

Quando uma regra é violada, a API responde `400` com a mensagem específica, e o frontend exibe num toast.
