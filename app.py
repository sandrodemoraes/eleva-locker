import os
import sys
from pathlib import Path

# Bancada: força SQLite ANTES de importar config (evita 0 armários após reinício)
_ROOT = Path(__file__).resolve().parent
_env_path = _ROOT / ".env"
if _env_path.exists():
    for _linha in _env_path.read_text(encoding="utf-8").splitlines():
        _t = _linha.strip().lower()
        if _t.startswith("eleva_bancada=") and _t.split("=", 1)[1].strip().split()[0] in (
            "1", "true", "yes",
        ):
            os.environ["ELEVA_BANCADA"] = "1"
            os.environ.pop("DATABASE_URL", None)
            break

from flask import Flask

from database import criar_banco
from services.backup.backup_service import BackupService

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.empresas import empresas_bp
from routes.armarios import armarios_bp
from routes.compartimentos import compartimentos_bp
from routes.encomendas import encomendas_bp
from routes.logs import logs_bp
from routes.esp32 import esp32_bp
from routes.totem import totem_bp
from routes.notificacoes import notificacoes_bp
from routes.planos import planos_bp
from routes.contratos import contratos_bp
from routes.faturas import faturas_bp
from routes.financeiro import financeiro_bp
from routes.portal import portal_bp
from routes.api.esp32_api import esp32_api_bp
from routes.api.compartimento_api import compartimento_api_bp
from routes.sites import sites_bp
from routes.relatorios import relatorios_bp
from routes.api.v1.public_api import v1_bp


app = Flask(__name__)

from config import SECRET_KEY, FLASK_DEBUG, avisar_segredos_padrao
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=86400 * 7,
)

criar_banco()

from db.connection import get_engine

_engine = get_engine()
print(f"Banco: {_engine.upper()}" + (" (bancada SQLite)" if _engine == "sqlite" else ""))
if _engine == "postgresql":
    print("=" * 50)
    print("  ERRO: PostgreSQL ativo na bancada!")
    print("  Feche este servidor e rode: tools\\consertar_bancada.bat")
    print("  Ou inicie sempre com: tools\\iniciar_tudo.bat")
    print("=" * 50)
elif _engine == "sqlite":
    try:
        from repositories.base_repository import BaseRepository
        with BaseRepository.get_connection() as _conn:
            _n = _conn.execute("SELECT COUNT(*) AS n FROM armarios").fetchone()["n"]
        if _n == 0:
            print("=" * 50)
            print("  AVISO: SQLite OK mas 0 armários no banco.")
            print("  Rode: tools\\consertar_bancada.bat")
            print("=" * 50)
    except Exception:
        pass

_seg = avisar_segredos_padrao()
if _seg:
    print("  (tools\\verificar_seguranca.bat — checklist completo)")

if os.getenv("SKIP_BACKUP") != "1":
    try:
        BackupService.criar_backup(forcar=True)
    except Exception as erro:
        print(f"⚠ Erro ao executar o backup: {erro}")

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(empresas_bp)
app.register_blueprint(armarios_bp)
app.register_blueprint(compartimentos_bp)
app.register_blueprint(encomendas_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(esp32_bp)
app.register_blueprint(totem_bp)
app.register_blueprint(notificacoes_bp)
app.register_blueprint(planos_bp)
app.register_blueprint(contratos_bp)
app.register_blueprint(faturas_bp)
app.register_blueprint(financeiro_bp)
app.register_blueprint(portal_bp)
app.register_blueprint(esp32_api_bp)
app.register_blueprint(compartimento_api_bp)
app.register_blueprint(sites_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(v1_bp)


def _iniciar_watchdog_esp32():
    """Marca ESP32 offline quando heartbeat expira (a cada 30s)."""
    import threading
    import time
    from repositories.esp32_repository import Esp32Repository

    def _loop():
        while True:
            time.sleep(30)
            try:
                Esp32Repository.marcar_offline_expirados()
            except Exception:
                pass

    threading.Thread(target=_loop, daemon=True, name="esp32-offline-watchdog").start()


_iniciar_watchdog_esp32()


@app.context_processor
def inject_site_context():
    from flask import session
    if "usuario_id" in session:
        from services.site_service import SiteService
        from middleware.site_scope import get_site_id
        from services.totem_ajuda_service import TotemAjudaService
        return {
            "sites": SiteService.listar_ativos(),
            "site_atual": get_site_id(),
            "ajuda_pendentes": TotemAjudaService.contar_pendentes(),
        }
    return {}


if __name__ == "__main__":
    from routes.totem import TOTEM_VERSAO
    print("=" * 50)
    print(f"  ELEVA LOCKER — Totem v{TOTEM_VERSAO}")
    print("  http://0.0.0.0:15000/totem/versao")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "15000")),
        debug=FLASK_DEBUG,
    )
