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
from routes.lgpd import lgpd_bp
from routes.lgpd_admin import lgpd_admin_bp


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
app.register_blueprint(lgpd_bp)
app.register_blueprint(lgpd_admin_bp)


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


def _iniciar_lgpd_retencao_diaria():
    """Retenção LGPD 1x/dia quando LGPD_JOB_ATIVO=1."""
    import threading
    import time

    intervalo_h = int(os.getenv("LGPD_JOB_INTERVALO_HORAS", "24"))

    def _loop():
        time.sleep(120)
        while True:
            try:
                import config as app_config
                if app_config.LGPD_JOB_ATIVO:
                    with app.app_context():
                        from services.lgpd_retencao_service import LgpdRetencaoService
                        r = LgpdRetencaoService.executar(simular=False)
                        print(
                            "[LGPD-RETENCAO] encomendas="
                            f"{r['encomendas']['elegiveis']} logs={r['logs']['elegiveis']}"
                        )
            except Exception as erro:
                print(f"[LGPD-RETENCAO] Erro: {erro}")
            time.sleep(max(1, intervalo_h) * 3600)

    if os.getenv("LGPD_JOB_ATIVO", "0") == "1":
        threading.Thread(target=_loop, daemon=True, name="lgpd-retencao").start()


_iniciar_lgpd_retencao_diaria()


@app.template_filter("lgpd_telefone")
def lgpd_telefone_filter(valor):
    from flask import session
    from services.lgpd_mascara_service import LgpdMascaraService
    return LgpdMascaraService.telefone_para_exibicao(valor, session.get("perfil"))


@app.template_filter("lgpd_destinatario")
def lgpd_destinatario_filter(valor):
    from flask import session
    from services.lgpd_mascara_service import LgpdMascaraService
    return LgpdMascaraService.texto_para_exibicao(valor, session.get("perfil"))


@app.context_processor
def inject_lgpd_ui():
    import config as app_config
    return {
        "lgpd_consentimento_usuario": app_config.LGPD_CONSENTIMENTO_USUARIO,
        "lgpd_politica_versao": app_config.LGPD_POLITICA_VERSAO,
    }


@app.context_processor
def inject_site_context():
    from flask import session
    import config as app_config
    if "usuario_id" in session:
        from services.site_service import SiteService
        from middleware.site_scope import get_site_id
        from services.totem_ajuda_service import TotemAjudaService
        pendentes = TotemAjudaService.contar_pendentes()
        return {
            "sites": SiteService.listar_ativos(),
            "site_atual": get_site_id(),
            "ajuda_totem_pendentes": pendentes,
            "lgpd_titular_ativo": app_config.LGPD_TITULAR_ATIVO,
        }
    return {}


if __name__ == "__main__":

    from tools.confirmar_parada import instalar_handler_parada, perguntar_encerramento

    instalar_handler_parada()

    print("ELEVA LOCKER | Ctrl+C pergunta S/N antes de encerrar")
    print("DEIXE ESTA JANELA ABERTA enquanto o totem estiver em uso.\n")

    while True:
        try:
            app.run(
                host="0.0.0.0",
                port=15000,
                debug=False,
                use_reloader=False,
            )
            break
        except KeyboardInterrupt:
            if perguntar_encerramento():
                print("Servidor encerrado.")
                break
            print("Servidor continua — reiniciando...\n")
        except SystemExit:
            break
