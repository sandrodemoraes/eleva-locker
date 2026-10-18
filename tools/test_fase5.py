#!/usr/bin/env python3
"""Testes automatizados — Fase 5 (e regressão geral)."""
import os
import sys

os.environ["SKIP_BACKUP"] = "1"
os.environ.setdefault("NOTIF_MODO", "console")
os.environ.setdefault("PAGAMENTO_MODO", "console")
os.environ.setdefault("ESP32_MODO_SIMULACAO", "1")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import criar_banco

criar_banco()

from app import app

PASS = 0
FAIL = 0


def ok(nome):
    global PASS
    PASS += 1
    print(f"  OK  {nome}")


def fail(nome, err):
    global FAIL
    FAIL += 1
    print(f"  FAIL {nome}: {err}")


def test(nome, fn):
    try:
        fn()
        ok(nome)
    except Exception as e:
        fail(nome, e)


client = app.test_client()


def login():
    return client.post("/login", data={
        "email": "admin@elevalocker.com",
        "senha": "123456",
    }, follow_redirects=True)


# --- Auth ---
def t_auth():
    r = login()
    assert r.status_code == 200
    assert b"Dashboard" in r.data or b"Bem-vindo" in r.data


# --- DB engine ---
def t_db_engine():
    from db.connection import get_engine
    assert get_engine() == "sqlite"


# --- Sites ---
def t_sites_list():
    login()
    r = client.get("/sites")
    assert r.status_code == 200
    assert b"Matriz ELEVA" in r.data or b"Sites" in r.data


def t_sites_criar():
    login()
    r = client.post("/sites/novo", data={
        "nome": "Franquia Teste",
        "codigo": "teste-franq",
        "cidade": "Rio de Janeiro",
        "estado": "RJ",
        "status": "1",
    }, follow_redirects=True)
    assert r.status_code == 200


def t_api_key():
    login()
    r = client.post("/sites/api-key/nova", data={
        "nome": "Key Teste",
        "site_id": "1",
        "permissoes": "write",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"elk_" in r.data


# --- API pública ---
def t_api_v1_status():
    from repositories.api_key_repository import ApiKeyRepository
    keys = ApiKeyRepository.listar()
    assert keys, "Precisa de chave API"
    chave = keys[-1]["chave"]
    r = client.get("/api/v1/status", headers={"X-API-Key": chave})
    assert r.status_code == 200
    data = r.get_json()
    assert data["sucesso"] is True


def t_api_v1_armarios():
    from repositories.api_key_repository import ApiKeyRepository
    chave = ApiKeyRepository.listar()[0]["chave"]
    r = client.get("/api/v1/armarios", headers={"X-API-Key": chave})
    assert r.status_code == 200
    assert r.get_json()["sucesso"] is True


def t_api_v1_sem_chave():
    r = client.get("/api/v1/status")
    assert r.status_code == 401


# --- Relatórios ---
def t_relatorios():
    login()
    r = client.get("/relatorios")
    assert r.status_code == 200
    assert b"Relat" in r.data


def t_relatorios_api():
    login()
    r = client.get("/relatorios/api/dados")
    assert r.status_code == 200
    data = r.get_json()
    assert "resumo" in data
    assert "previsao" in data


# --- Multi-site selector ---
def t_site_selecionar():
    login()
    r = client.post("/sites/selecionar", data={"site_id": "1"}, follow_redirects=True)
    assert r.status_code == 200


# --- Regressão rápida ---
def t_dashboard():
    login()
    r = client.get("/dashboard")
    assert r.status_code == 200


def t_armarios():
    login()
    assert client.get("/armarios").status_code == 200


def t_encomendas():
    login()
    assert client.get("/encomendas").status_code == 200


def t_financeiro():
    login()
    assert client.get("/financeiro").status_code == 200


def t_totem():
    assert client.get("/totem").status_code == 200


def t_esp32_api():
    from repositories.esp32_repository import Esp32Repository
    import config
    esp = Esp32Repository.listar()
    if esp and esp[0].get("token"):
        token = esp[0]["token"]
    else:
        token = config.ESP32_TOKEN
    r = client.post("/api/esp32/heartbeat", json={"ip": "127.0.0.1"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (200, 400)


def t_relatorio_service():
    from services.relatorio_service import RelatorioService
    dados = RelatorioService.dados_completos()
    assert "taxa_ocupacao" in dados["resumo"]
    assert len(dados["previsao"]["previsao"]) == 7


TESTS = [
    ("Auth login", t_auth),
    ("DB engine SQLite", t_db_engine),
    ("Sites listagem", t_sites_list),
    ("Sites criar", t_sites_criar),
    ("API key criar", t_api_key),
    ("API v1 status", t_api_v1_status),
    ("API v1 armários", t_api_v1_armarios),
    ("API v1 sem chave", t_api_v1_sem_chave),
    ("Relatórios página", t_relatorios),
    ("Relatórios JSON", t_relatorios_api),
    ("Site selecionar", t_site_selecionar),
    ("Dashboard", t_dashboard),
    ("Armários", t_armarios),
    ("Encomendas", t_encomendas),
    ("Financeiro", t_financeiro),
    ("Totem", t_totem),
    ("RelatorioService", t_relatorio_service),
]

if __name__ == "__main__":
    print("ELEVA LOCKER — Testes Fase 5\n")
    for nome, fn in TESTS:
        test(nome, fn)
    print(f"\nResultado: {PASS}/{PASS + FAIL} passaram")
    if FAIL:
        sys.exit(1)
