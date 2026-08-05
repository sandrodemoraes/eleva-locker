-- Schema PostgreSQL — ELEVA LOCKER (Fase 5)
-- Preferir: python database.py (via criar_banco com DATABASE_URL)
-- Ou: psql -f database/schema_postgres.sql

-- Este arquivo documenta o schema; a inicialização é feita automaticamente pelo app.

CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    codigo TEXT UNIQUE,
    endereco TEXT,
    cidade TEXT,
    estado TEXT,
    status INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(id),
    nome TEXT NOT NULL,
    chave TEXT UNIQUE NOT NULL,
    permissoes TEXT DEFAULT 'read',
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demais tabelas são criadas por database.criar_banco() na primeira execução.
