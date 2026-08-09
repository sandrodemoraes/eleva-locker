from flask import Flask
import os

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

from config import SECRET_KEY
app.secret_key = SECRET_KEY

criar_banco()

from db.connection import get_engine

_engine = get_engine()
print(f"Banco: {_engine.upper()}" + (" (bancada SQLite)" if _engine == "sqlite" else ""))
if _engine == "postgresql" and os.getenv("ELEVA_BANCADA", "").strip() not in ("1", "true", "yes"):
    print("⚠ AVISO: PostgreSQL ativo — na bancada defina ELEVA_BANCADA=1 no .env")

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


@app.context_processor
def inject_site_context():
    from flask import session
    if "usuario_id" in session:
        from services.site_service import SiteService
        from middleware.site_scope import get_site_id
        return {
            "sites": SiteService.listar_ativos(),
            "site_atual": get_site_id(),
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
        port=15000,
        debug=True
    )
