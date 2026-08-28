import os
from werkzeug.security import generate_password_hash

from db.connection import (
    get_connection, get_engine, coluna_existe, adicionar_coluna, adapt_ddl,
)

DB_PATH = os.path.join("database", "elevalocker.db")


def conectar():
    return get_connection()


def criar_banco():

    os.makedirs("database", exist_ok=True)

    engine = get_engine()
    conn = get_connection()
    cursor = conn.cursor()

    def ddl(sql):
        cursor.execute(adapt_ddl(sql, engine))

    # ============================
    # TABELA USUÁRIOS
    # ============================
    ddl("""
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
    ddl("""
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
    ddl("""
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
    ddl("""
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
    ddl("""
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
    ddl("""
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
    ddl("""
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
    adicionar_coluna(cursor, "armarios", "empresa_id", "INTEGER")
    adicionar_coluna(cursor, "compartimentos", "tamanho", "TEXT DEFAULT 'M'")
    adicionar_coluna(cursor, "encomendas", "operador", "TEXT")
    adicionar_coluna(cursor, "encomendas", "transportadora", "TEXT")
    adicionar_coluna(cursor, "encomendas", "observacao", "TEXT")

    # Migrações Fase 2 — ESP32
    adicionar_coluna(cursor, "esp32", "token", "TEXT")
    adicionar_coluna(cursor, "esp32", "porta", "INTEGER DEFAULT 80")
    adicionar_coluna(cursor, "esp32", "ultimo_heartbeat", "DATETIME")

    # Migrações Fase 3 — Notificações
    adicionar_coluna(cursor, "encomendas", "notificado_em", "DATETIME")
    adicionar_coluna(cursor, "encomendas", "expira_em", "DATETIME")
    adicionar_coluna(cursor, "encomendas", "retida_em", "DATETIME")
    adicionar_coluna(cursor, "encomendas", "ultimo_lembrete_em", "DATETIME")

    cursor.execute("""
        UPDATE encomendas
        SET expira_em = datetime(data_entrada, '+3 days')
        WHERE expira_em IS NULL
          AND status IN ('aguardando_retirada', 'retida')
          AND data_entrada IS NOT NULL
          AND data_entrada != ''
    """)

    ddl("""
    CREATE TABLE IF NOT EXISTS notificacoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        encomenda_id INTEGER,
        canal TEXT,
        destinatario TEXT,
        mensagem TEXT,
        status TEXT,
        detalhe TEXT,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
        UPDATE esp32 SET status = 'offline'
        WHERE status IS NULL OR status = ''
    """)

    cursor.execute("""
        UPDATE armarios SET status = 'ativo'
        WHERE status IS NULL OR status = ''
    """)

    cursor.execute("""
        UPDATE compartimentos SET status = 'livre'
        WHERE status IS NULL OR status = ''
    """)

    # ============================
    # FASE 4 — COMERCIAL
    # ============================
    ddl("""
    CREATE TABLE IF NOT EXISTS planos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco_mensal REAL NOT NULL,
        max_armarios INTEGER DEFAULT -1,
        max_compartimentos INTEGER DEFAULT -1,
        max_encomendas_mes INTEGER DEFAULT -1,
        inclui_whatsapp INTEGER DEFAULT 0,
        inclui_relatorios INTEGER DEFAULT 1,
        status INTEGER DEFAULT 1,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    ddl("""
    CREATE TABLE IF NOT EXISTS contratos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER NOT NULL,
        plano_id INTEGER NOT NULL,
        data_inicio TEXT NOT NULL,
        data_fim TEXT,
        status TEXT DEFAULT 'ativo',
        valor_mensal REAL NOT NULL,
        renovacao_automatica INTEGER DEFAULT 1,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    ddl("""
    CREATE TABLE IF NOT EXISTS faturas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contrato_id INTEGER NOT NULL,
        referencia TEXT NOT NULL,
        valor REAL NOT NULL,
        status TEXT DEFAULT 'pendente',
        data_vencimento TEXT,
        data_pagamento TEXT,
        link_pagamento TEXT,
        gateway_id TEXT,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    adicionar_coluna(cursor, "usuarios", "empresa_id", "INTEGER")

    # FASE 5 — ESCALA
    ddl("""
    CREATE TABLE IF NOT EXISTS sites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        codigo TEXT UNIQUE,
        endereco TEXT,
        cidade TEXT,
        estado TEXT,
        status INTEGER DEFAULT 1,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    ddl("""
    CREATE TABLE IF NOT EXISTS api_keys(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id INTEGER,
        nome TEXT NOT NULL,
        chave TEXT UNIQUE NOT NULL,
        permissoes TEXT DEFAULT 'read',
        ativo INTEGER DEFAULT 1,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    adicionar_coluna(cursor, "empresas", "site_id", "INTEGER")
    adicionar_coluna(cursor, "armarios", "site_id", "INTEGER")

    cursor.execute("SELECT COUNT(*) AS c FROM sites")
    rs = cursor.fetchone()
    n_sites = list(rs.values())[0] if hasattr(rs, "values") else rs[0]
    if n_sites == 0:
        cursor.execute("""
            INSERT INTO sites (nome, codigo, cidade, estado)
            VALUES ('Matriz ELEVA', 'matriz', 'São Paulo', 'SP')
        """)

    # Planos padrão
    cursor.execute("SELECT COUNT(*) AS c FROM planos")
    rs = cursor.fetchone()
    n_planos = list(rs.values())[0] if hasattr(rs, "values") else rs[0]
    if n_planos == 0:
        cursor.executemany("""
            INSERT INTO planos (
                nome, descricao, preco_mensal,
                max_armarios, max_compartimentos, max_encomendas_mes,
                inclui_whatsapp, inclui_relatorios
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("Starter", "Ideal para condomínios pequenos", 199.0, 1, 20, 500, 0, 1),
            ("Profissional", "Até 5 armários", 499.0, 5, 100, 2000, 1, 1),
            ("Enterprise", "Recursos ilimitados", 1499.0, -1, -1, -1, 1, 1),
        ])

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

    print(f"Banco criado com sucesso ({get_engine()}).")