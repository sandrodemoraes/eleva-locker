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


app = Flask(__name__)
app.secret_key = "ElevaLocker2026"


criar_banco()

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(empresas_bp)
app.register_blueprint(armarios_bp)
app.register_blueprint(compartimentos_bp)
app.register_blueprint(encomendas_bp)
app.register_blueprint(logs_bp)


if __name__ == "__main__":

    try:
        BackupService.criar_backup()
    except Exception as erro:
        print(f"⚠ Erro ao executar o backup: {erro}")

    app.run(
        host="0.0.0.0",
        port=15000,
        debug=True
    )
