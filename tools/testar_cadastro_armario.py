"""Simula cadastro de morador no armário."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from app import app
import config


def _login_admin(client):
    with app.app_context():
        from database import conectar
        from werkzeug.security import generate_password_hash
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email='admin@test.local'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO usuarios (nome,email,telefone,senha,perfil,status) VALUES (?,?,?,?,?,?)",
                ("Admin Teste", "admin@test.local", "48999990000",
                 generate_password_hash("admin123"), "Administrador", 1),
            )
            conn.commit()
        conn.close()
    client.post("/login", data={"email": "admin@test.local", "senha": "admin123"})


def test_ok():
    client = app.test_client()
    _login_admin(client)
    email = "sandra.armario.test@local.dev"
    with app.app_context():
        from database import conectar
        conn = conectar()
        conn.execute("DELETE FROM usuarios WHERE email=?", (email,))
        conn.commit()
        conn.close()

    data = {
        "nome": "Sandra Teste",
        "email": email,
        "telefone": "48999887766",
        "senha": "senha123",
        "confirmar": "senha123",
        "perfil": "Usuário",
        "status": "1",
    }
    if config.LGPD_CONSENTIMENTO_USUARIO:
        data["lgpd_consentimento"] = "1"

    r = client.post("/armarios/2/usuarios/novo", data=data, follow_redirects=False)
    assert r.status_code == 302
    assert "modal=novo_usuario" not in (r.location or ""), "cadastro deveria ter sucesso"
    print("OK cadastro morador armário 2")


def test_erro_reabre_modal():
    client = app.test_client()
    _login_admin(client)
    data = {
        "nome": "X",
        "email": "invalido",
        "telefone": "",
        "senha": "a",
        "confirmar": "b",
        "perfil": "Usuário",
        "status": "1",
    }
    r = client.post("/armarios/2/usuarios/novo", data=data, follow_redirects=False)
    assert r.status_code == 302
    assert "modal=novo_usuario" in (r.location or "")
    print("OK erro redireciona com modal=novo_usuario")


if __name__ == "__main__":
    print("LGPD_CONSENTIMENTO_USUARIO =", config.LGPD_CONSENTIMENTO_USUARIO)
    test_ok()
    test_erro_reabre_modal()
    print("Todos os testes passaram.")
