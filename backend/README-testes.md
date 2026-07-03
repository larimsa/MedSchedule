# QA do MedSchedule — Relatório de Validação e Verificação de Software

Este documento explica a suíte de testes criada em `backend/tests/`, por que ela
está organizada do jeito que está, e como cada aula da disciplina se manifesta
no código. A ideia não foi só "escrever testes", mas seguir de propósito a
Pirâmide de Testes do talk do Otavio Lemos (slides em anexo) e as técnicas
vistas ao longo do semestre.

## 1. Por que services.py é o centro de tudo

Antes de falar de testes, vale entender uma decisão de arquitetura que o
MedSchedule já tinha e que facilitou (e muito) a vida do QA: `services.py`
concentra **toda** regra de negócio em funções puras — sem tocar banco,
sem `datetime.now()` implícito sem opção de override, sem I/O.

Isso é exatamente o "Functional Core, Imperative Shell" que aparece nos
slides finais do PDF da Aula 10 (Scott Wlaschin / talk do Otavio Lemos):

```
routers/*.py  (Imperative Shell — I/O: banco, HTTP)
      │
      ▼
services.py   (Functional Core — deterministico, sem I/O)
```

Na prática isso significa: **a maior parte das regras pode — e deve — ser
testada como unidade**, sem precisar de FastAPI, banco ou rede. Só as poucas
regras que realmente dependem de *consultar o estado do banco* (conflito de
horário, paciente duplicado, limite diário, histórico de retorno) ficam nos
routers e por isso só podem ser testadas com integração.

## 2. A pirâmide aplicada ao projeto

```
tests/
├── unit/          131 testes   (base — rápidos, IO-Free)
├── integration/    39 testes   (meio — IO-dependent, banco SQLite real)
├── doubles/          3 testes  (dublês/mocks — Aula 13)
└── e2e/              2 testes  (topo — poucos, caros, caminhos críticos)
                  ─────────────────
                  175 testes · 100% cobertura de linha em services/routers/models/schemas
                  ~1,5s a suíte inteira
```

| Camada | O que testa | Como | Por quê está aí |
|---|---|---|---|
| `tests/unit/` (131) | `services.py` — todas as regras de negócio puras | chama a função diretamente, sem banco | são IO-Free → "se não roda rápido, não é teste de unidade" (slide do Michael Feathers no PDF) |
| `tests/integration/` (39) | `routers/*.py` — CRUD, filtros, cobrança | `TestClient` + SQLite **real** em memória (fixture `client`) | conflito de horário, duplicidade de paciente, limite diário e regra de retorno só existem consultando o banco — não dá pra isolar em unidade sem reimplementar a query |
| `tests/doubles/` (3) | Isolamento do router com `Session` mockada | `unittest.mock.MagicMock` no lugar do SQLAlchemy | Aula 13 — mostra a diferença entre teste "solitário" (mock) e "sociável" (banco real), incluindo o trade-off que o próprio slide do Otavio Lemos cita ("Problem with solitary tests") |
| `tests/e2e/` (2) | Jornada completa via HTTP | `client` fim-a-fim | só os 2 caminhos que, se quebrarem, tiram a clínica do ar: cadastro→agendamento→cobrança→retorno→cancelamento, e o health-check |

A proporção 131 : 39 : 3 : 2 não foi escolhida a dedo — ela é consequência
direta de quanta regra de negócio é pura (unit) vs. quanta depende do banco
(integration). É literalmente o "link entre proporção de testes e design de
software" que está na promessa do talk.

## 3. Mapeamento com as aulas da disciplina

| Aula | Onde aparece na suíte |
|---|---|
| **1 — Fundamentos & Pytest** | `pytest.ini` (markers, `pythonpath`), estrutura `tests/`, fixtures em `conftest.py` |
| **2 — Teste Funcional** | Todo `tests/unit/` e `tests/integration/` testam comportamento observável (levanta erro? retorna 201/400/404?), não a implementação interna |
| **3 — Motivando o Teste de Software** | `README-testes.md` (este arquivo) — ligação entre confiança no código e agilidade para mexer nas regras de agendamento |
| **4 — Análise de Valor Limite / Classes de Equivalência** | `test_validacoes_formato.py`, `test_regras_agendamento.py`, `test_regra_retorno.py` — todas as bordas testadas explicitamente (08:00/18:00, múltiplos de 30min, 60min de antecedência, 30 dias de retorno, 4–6 dígitos de CRM) |
| **5 — Caso realístico (rate limiter)** | Inspirou o padrão usado em `TestValidarAntecedencia` (janela de tempo com borda testada nos dois lados) |
| **6/7 — Teste Estrutural & Cobertura** | `pytest-cov` configurado; usado para achar 3 branches não cobertos (filtro por `tipo`/`data`, conflito no `PUT`, email inválido no `PUT` de médico) e fechar 100% de cobertura de linha — igual ao processo iterativo do exemplo `leftPad`/JaCoCo do PDF |
| **9 — Teste de Mutação** | `setup.cfg` ([mutmut]) + seção 5 deste relatório |
| **10 — Pirâmide e tipos de teste** | Toda a estrutura de diretórios `tests/unit` / `tests/integration` / `tests/e2e`, e a separação Functional Core / Imperative Shell descrita acima |
| **13 — Dublês de teste / Mock** | `tests/doubles/test_mocks_e_dubles.py` — mock de `Session` (solitary test) e stub de `datetime.now()` |

## 4. Como rodar

```bash
cd backend
pip install -r requirements-test.txt

# suíte inteira
pytest

# só uma camada da pirâmide (markers definidos em pytest.ini)
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m mock

# com cobertura
pytest --cov=services --cov=routers --cov=models --cov=schemas --cov-report=term-missing

# teste de mutação (mira services.py, ~15-20s)
mutmut run
mutmut results
mutmut show <id-do-mutante>   # ver o diff de um mutante específico
```

## 5. Resultado do teste de mutação

`mutmut` mira `services.py` (o "functional core") rodando contra
`tests/unit/` + `tests/doubles/`, que são as camadas que exercitam essas
funções diretamente.

**194 mutantes gerados → 159 mortos → 35 sobreviventes (~82% de mutation
score).**

Ao investigar os sobreviventes com `mutmut show`, eles caem em dois grupos:

1. **3 mutantes de lógica real, corrigidos durante este trabalho:**
   - `alvo < agora` → `alvo <= agora` em `validar_antecedencia` (mudava o
     comportamento exatamente quando o horário pedido é igual a "agora").
   - `not parte or "-" not in parte` → `... and ...` em
     `validar_horario_medico` (fazia a função aceitar qualquer horário
     quando uma janela mal formatada aparecia no meio de uma janela válida).
   - `continue` → `break` no mesmo loop (uma janela inválida antes de uma
     válida derrubava a validação inteira).

   Cada um ganhou um teste dedicado com o comentário `# Teste de mutação:`
   explicando exatamente qual comportamento diferencia o código original do
   mutante — essa é a "hipótese do programador competente" na prática: o
   mutante representa um erro plausível (uma trocinha de operador) que a
   cobertura de linha, sozinha, nunca teria pego (as linhas já estavam 100%
   cobertas antes desses testes).

2. **32 mutantes remanescentes, todos de conteúdo literal de string**
   (mensagens de erro como `"Data inválida"` → `"DATA INVÁLIDA"` ou
   `RegraNegocioError(None)`). Decisão consciente de não persegui-los:
   nenhum deles muda o *comportamento* da API (o `status_code` continua
   400/404, e o texto exato da mensagem de erro não é contrato da API para
   o frontend — ele só aparece num toast informativo). Matar 100% desses
   mutantes exigiria `match=` exato em toda mensagem de erro do sistema, o
   que deixaria os testes frágeis a qualquer reformulação de texto sem
   ganho real de detecção de defeitos. Esse é justamente o ponto do slide
   final do PDF da Aula 9: métricas de mutação "devem ser interpretadas com
   critério técnico", não perseguidas como um número absoluto.

## 6. Cobertura de código

```
Name                   Stmts   Miss  Cover
----------------------------------------------------
models.py                 32      0   100%
routers/__init__.py        0      0   100%
routers/consultas.py      90      0   100%
routers/medicos.py        54      0   100%
schemas.py                54      0   100%
services.py              113      0   100%
----------------------------------------------------
TOTAL                    343      0   100%
```

Importante: 100% de cobertura de linha **não** significa "sem bugs" — foi
justamente o teste de mutação (seção 5) que mostrou 3 bugs plausíveis
escondidos atrás de linhas já 100% cobertas. Os dois números contam
histórias diferentes e complementares, como visto na Aula 7.

## 7. Estrutura final

```
backend/
├── pytest.ini                          # markers + pythonpath
├── setup.cfg                           # config do mutmut
├── requirements-test.txt               # deps de teste (pytest, cov, mutmut, httpx)
└── tests/
    ├── conftest.py                     # fixtures: banco SQLite de teste, TestClient, helpers
    ├── unit/
    │   ├── test_validacoes_formato.py  # Aula 4: data, hora, email, CRM, tipo
    │   ├── test_regras_agendamento.py  # Aula 4/6/7: expediente, intervalo, fim de semana,
    │   │                               #   antecedência, horário do médico
    │   ├── test_regra_retorno.py       # Aula 4: janela de 30 dias
    │   ├── test_calculos.py            # preço, duração, hora de fim, desconto
    │   └── test_orquestrador.py        # Aula 2: validar_agendamento (teste funcional)
    ├── integration/
    │   ├── test_medicos_router.py      # CRUD de médicos
    │   ├── test_consultas_router.py    # CRUD de consultas + cobrança
    │   └── test_consultas_regras_com_banco.py  # conflito, duplicidade, limite, retorno
    ├── doubles/
    │   └── test_mocks_e_dubles.py      # Aula 13: mock de Session, stub de datetime
    └── e2e/
        └── test_fluxos_criticos.py     # os 2 caminhos críticos ponta-a-ponta
```
