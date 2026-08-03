from flask import Flask

from database import criar_banco
from services.backup.backup_service import BackupService

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.empresas import empresas_bp
from routes.armarios import armarios_bp


app = Flask(__name__)
app.secret_key = "ElevaLocker2026"


# ==========================================
# Inicialização do banco de dados
# ==========================================

criar_banco()


# ==========================================
# Registro dos Blueprints
# ==========================================

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(empresas_bp)
app.register_blueprint(armarios_bp)


# ==========================================
# Mostrar todas as rotas registradas
# ==========================================

print("\n====================================")
print("ROTAS REGISTRADAS")
print("====================================")

for regra in app.url_map.iter_rules():
    print(f"{regra.rule} -> {regra.methods}")

print("====================================\n")


# ==========================================
# Inicialização da aplicação
# ==========================================

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