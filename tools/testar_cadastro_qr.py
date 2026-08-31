"""Testa cadastro público e QR code (sem subir servidor)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SKIP_BACKUP", "1")
os.environ.setdefault("CADASTRO_PUBLICO_ATIVO", "1")

from app import app
from services.qrcode_service import QrcodeService
from services.cadastro_publico_service import CadastroPublicoService


def test_qrcode_url():
    png = QrcodeService.gerar_png_url("http://localhost:15000/cadastro")
    data = png.read()
    assert len(data) > 500, "PNG QR muito pequeno"
    print("OK qrcode URL PNG", len(data), "bytes")


def test_rotas():
    client = app.test_client()
    r = client.get("/cadastro")
    assert r.status_code == 200, f"/cadastro status {r.status_code}"
    assert b"Cadastre seu condom" in r.data
    print("OK GET /cadastro")

    r = client.get("/cadastro/qrcode.png")
    assert r.status_code == 200
    assert r.mimetype == "image/png"
    print("OK GET /cadastro/qrcode.png")

    url = CadastroPublicoService.url_cadastro()
    assert url.endswith("/cadastro")
    print("OK url_cadastro:", url)


if __name__ == "__main__":
    test_qrcode_url()
    test_rotas()
    print("\nTodos os testes passaram.")
