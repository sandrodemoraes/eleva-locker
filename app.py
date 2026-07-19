from flask import Flask
from database import criar_banco
from services.backup.backup_service import BackupService
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.empresas import empresas_bp

app = Flask(__name__)
app.secret_key = "ElevaLocker2026"

criar_banco()

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(empresas_bp)

if __name__ == "__main__":

    BackupService.criar_backup()

    app.run(
        host="0.0.0.0",
        port=15000,
        debug=True
    )