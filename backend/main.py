# ─────────────────────────────────────────────
# main.py — Entry point da API MedSchedule
# ─────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
import models
from routers import medicos, consultas

# Cria as tabelas no banco automaticamente ao iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedSchedule API",
    description="API de agendamento médico para a clínica MedSchedule",
    version="1.0.0"
)

# ── CORS ─────────────────────────────────────
# Permite que o frontend (Static Site) chame a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Em produção, troque pelo domínio do seu Static Site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ──────────────────────────────────
app.include_router(medicos.router)
app.include_router(consultas.router)


# ── ROTA RAIZ ────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "app":    "MedSchedule API",
        "docs":   "/docs"
    }


# ── HEALTH CHECK ─────────────────────────────
@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
