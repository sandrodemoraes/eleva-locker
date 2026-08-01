import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join("database", "elevalocker.db")


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cursor.fetchall())


def _adicionar_coluna(cursor, tabela, coluna, definicao):
    if not _coluna_existe(cursor, tabela, coluna):
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")


def criar_banco():

    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ============================
    # TABELA USUÁRIOS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        email TEXT NOT NULL UNIQUE,

        senha TEXT NOT NULL,

        telefone TEXT,

        perfil TEXT NOT NULL DEFAULT 'Operador',

        status INTEGER NOT NULL DEFAULT 1,

        ultimo_login DATETIME,

        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,

        data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ============================
    # TABELA EMPRESAS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresas(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        razao_social TEXT NOT NULL,

        nome_fantasia TEXT,

        cnpj TEXT UNIQUE,

        inscricao_estadual TEXT,

        responsavel TEXT,

        telefone TEXT,

        whatsapp TEXT,

        email TEXT,

        cep TEXT,

        endereco TEXT,

        numero TEXT,

        bairro TEXT,

        cidade TEXT,

        estado TEXT,

        status INTEGER DEFAULT 1,

        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ============================
    # TABELA ARMÁRIOS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS armarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        endereco TEXT,
        cidade TEXT,
        estado TEXT,
        status TEXT
    )
    """)

    # ============================
    # TABELA ESP32
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS esp32(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        ip TEXT,
        mac TEXT,
        armario INTEGER,
        status TEXT
    )
    """)

    # ============================
    # TABELA COMPARTIMENTOS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compartimentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        armario INTEGER,
        numero INTEGER,
        rele INTEGER,
        esp32_id INTEGER,
        status TEXT
    )
    """)

    # ============================
    # TABELA ENCOMENDAS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS encomendas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        cliente TEXT,
        telefone TEXT,
        email TEXT,
        compartimento INTEGER,
        data_entrada TEXT,
        data_retirada TEXT,
        status TEXT
    )
    """)

    # ============================
    # TABELA LOGS
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compartimento INTEGER,
        usuario TEXT,
        data TEXT,
        acao TEXT
    )
    """)

    # ============================
    # MIGRAÇÕES (Fase 1)
    # ============================
    _adicionar_coluna(cursor, "armarios", "empresa_id", "INTEGER")
    _adicionar_coluna(cursor, "compartimentos", "tamanho", "TEXT DEFAULT 'M'")
    _adicionar_coluna(cursor, "encomendas", "operador", "TEXT")
    _adicionar_coluna(cursor, "encomendas", "transportadora", "TEXT")
    _adicionar_coluna(cursor, "encomendas", "observacao", "TEXT")

    cursor.execute("""
        UPDATE armarios SET status = 'ativo'
        WHERE status IS NULL OR status = ''
    """)

    cursor.execute("""
        UPDATE compartimentos SET status = 'livre'
        WHERE status IS NULL OR status = ''
    """)

    # ============================
    # USUÁRIO ADMINISTRADOR PADRÃO
    # ============================
    cursor.execute("""
    SELECT id FROM usuarios
    WHERE email = ?
    """, ("admin@elevalocker.com",))

    admin = cursor.fetchone()

    if not admin:

        senha_hash = generate_password_hash("123456")

        cursor.execute("""
        INSERT INTO usuarios
        (
            nome,
            email,
            senha,
            telefone,
            perfil,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Administrador",
            "admin@elevalocker.com",
            senha_hash,
            "",
            "Administrador",
            1
        ))

    conn.commit()
    conn.close()

    print("Banco criado com sucesso.")