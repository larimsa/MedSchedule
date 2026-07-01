# ─────────────────────────────────────────────
# database.py — Conexão com o banco de dados
# ─────────────────────────────────────────────

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback: SQLite local quando não há DATABASE_URL (dev/testes sem Supabase).
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./medschedule.db"

# Render/Supabase às vezes entregam URL com "postgres://"; SQLAlchemy quer "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência usada nas rotas para obter uma sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
