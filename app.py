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
from routes.api.esp32_api import esp32_api_bp
from routes.api.compartimento_api import compartimento_api_bp


app = Flask(__name__)

from config import SECRET_KEY
app.secret_key = SECRET_KEY

criar_banco()

# Backup automático antes de iniciar (forçado na Fase 2+)
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
app.register_blueprint(esp32_api_bp)
app.register_blueprint(compartimento_api_bp)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=15000,
        debug=True
    )
