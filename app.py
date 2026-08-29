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


def _iniciar_lembretes_automaticos():
    """Verifica encomendas >24h no armário e reenvia notificação (a cada 30 min)."""
    import threading
    import time

    intervalo = int(os.getenv("ENCOMENDA_LEMBRETE_INTERVALO_MIN", "30"))

    def _loop():
        time.sleep(60)
        while True:
            try:
                with app.app_context():
                    from services.encomenda_service import EncomendaService
                    r = EncomendaService.processar_lembretes_automaticos()
                    if r["enviados"]:
                        print(f"[LEMBRETE] {r['enviados']} notificação(ões) reenviada(s)")
            except Exception as erro:
                print(f"[LEMBRETE] Erro: {erro}")
            time.sleep(max(5, intervalo) * 60)

    if os.getenv("ENCOMENDA_LEMBRETE_AUTOMATICO", "1") == "1":
        threading.Thread(target=_loop, daemon=True, name="lembretes-encomenda").start()


_iniciar_lembretes_automaticos()


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

    print("Ctrl+C pede confirmacao antes de encerrar (S/N).")
    print("DEIXE ESTA JANELA ABERTA enquanto o totem estiver em uso.\n")

    while True:
        try:
            app.run(
                host="0.0.0.0",
                port=15000,
                debug=True,
                use_reloader=False,
            )
            break
        except KeyboardInterrupt:
            print("\n")
            try:
                resp = input("Encerrar o servidor ELEVA LOCKER? (S/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                resp = "s"
            if resp in ("s", "sim", "y", "yes"):
                print("Servidor encerrado.")
                break
            print("Servidor continua — reiniciando...\n")
