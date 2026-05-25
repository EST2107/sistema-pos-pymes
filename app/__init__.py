from flask import Flask

from app.config.config import Config
from app.extensions import db, migrate, login_manager

from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.producto_routes import producto_bp
from app.routes.venta_routes import venta_bp
from app.routes.compra_routes import compra_bp
from app.routes.inventario_routes import inventario_bp
from app.routes.reporte_routes import reporte_bp
from app.routes.proveedor_routes import proveedor_bp
from app.routes.usuario_routes import usuario_bp
from app.routes.configuracion_routes import configuracion_bp

from app.models import Usuario


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    @app.context_processor
    def inject_empresa():
        from flask_login import current_user
        from app.models import Empresa
        if current_user.is_authenticated and current_user.id_empresa:
            empresa = Empresa.query.get(current_user.id_empresa)
            return dict(empresa_actual=empresa)
        return dict(empresa_actual=None)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(compra_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reporte_bp)
    app.register_blueprint(proveedor_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(configuracion_bp)

    return app