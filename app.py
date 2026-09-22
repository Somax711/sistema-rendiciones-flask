import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, jsonify
from flask_login import current_user
from config import get_config
from extensions import limiter
from models import db, login_manager, User
from utils.filters import register_filters
from routes.download import download_bp


# ─────────────────────────────────────────────────────────────
# Configuración de Logging
# ─────────────────────────────────────────────────────────────
def _configure_logging(app):
    """Configura logging a archivo para producción."""
    if app.debug or app.testing:
        return

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'sistema_rendiciones.log'),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Sistema de Rendiciones - Inicio')


# ─────────────────────────────────────────────────────────────
# Manejadores de Errores
# ─────────────────────────────────────────────────────────────
def _register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return '<h1>403 - Acceso denegado</h1><a href="/">Volver al inicio</a>', 403

    @app.errorhandler(404)
    def not_found(e):
        return '<h1>404 - Página no encontrada</h1><a href="/">Volver al inicio</a>', 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f'Error 500: {e}')
        try:
            db.session.rollback()
        except Exception:
            pass
        return '<h1>500 - Error interno del servidor</h1><a href="/">Volver al inicio</a>', 500


# ─────────────────────────────────────────────────────────────
# Factory de la Aplicación
# ─────────────────────────────────────────────────────────────
def create_app():
    """Factory para crear la aplicación Flask."""
    app = Flask(__name__)

    # Cargar configuración
    config = get_config()
    app.config.from_object(config)

    # Base de datos — Railway/Render inyectan DATABASE_URL
    db_url = os.environ.get("DATABASE_URL", "sqlite:///rendiciones.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # ─────────────────────────────────────────────────────────
    # Seguridad HTTP (Talisman) — solo activo en producción
    # ─────────────────────────────────────────────────────────
    is_production = os.environ.get("FLASK_ENV") == "production"
    if is_production:
        from flask_talisman import Talisman
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'img-src': ["'self'", "data:", "https:"],
                'script-src': [
                    "'self'", "'unsafe-inline'",
                    "https://cdn.jsdelivr.net",
                    "https://code.jquery.com",
                    "https://cdnjs.cloudflare.com",
                ],
                'style-src': [
                    "'self'", "'unsafe-inline'",
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com",
                ],
                'font-src': ["'self'", "https://cdnjs.cloudflare.com", "data:"],
            }
        )

    # Logging
    _configure_logging(app)

    # ─────────────────────────────────────────────────────────
    # Login Manager
    # ─────────────────────────────────────────────────────────
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return None
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # ─────────────────────────────────────────────────────────
    # Carpetas necesarias
    # ─────────────────────────────────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'comprobantes'), exist_ok=True)

    # ─────────────────────────────────────────────────────────
    # Blueprints
    # ─────────────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.rendiciones import rendiciones_bp
    from routes.aprobaciones import aprobaciones_bp
    from routes.usuarios import usuarios_bp
    from routes.reportes import reportes_bp
    from routes.notificaciones import notificaciones_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rendiciones_bp)
    app.register_blueprint(aprobaciones_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(notificaciones_bp)
    app.register_blueprint(download_bp)

    # ─────────────────────────────────────────────────────────
    # Rate limiting específico para login (anti-fuerza bruta)
    # 5 intentos por minuto por IP
    # ─────────────────────────────────────────────────────────
    if 'auth.login' in app.view_functions:
        original_login = app.view_functions['auth.login']
        app.view_functions['auth.login'] = limiter.limit("5 per minute")(original_login)

    # Filtros personalizados
    register_filters(app)

    # Manejadores de errores
    _register_error_handlers(app)

    # ─────────────────────────────────────────────────────────
    # Context processor
    # ─────────────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        notificaciones_count = 0
        if current_user.is_authenticated:
            try:
                notificaciones_count = current_user.get_notificaciones_no_leidas()
            except Exception:
                notificaciones_count = 0
        return {
            'notificaciones_count': notificaciones_count,
            'app_name': 'Sistema de Rendiciones Primar'
        }

    # ─────────────────────────────────────────────────────────
    # Health check (útil para Railway/Render)
    # ─────────────────────────────────────────────────────────
    @app.route('/health')
    @limiter.exempt
    def health():
        return jsonify({'status': 'ok'}), 200

    # ─────────────────────────────────────────────────────────
    # Ruta temporal para crear admin en producción
    # ⚠️  ELIMINAR después del primer uso
    # ─────────────────────────────────────────────────────────
    @app.route('/setup-admin-primar')
    @limiter.exempt
    def setup_admin():
        try:
            db.create_all()
            admin = User.query.filter_by(email='admin@primar.cl').first()
            if not admin:
                admin = User(
                    nombre='Administrador',
                    email='admin@primar.cl',
                    rol='admin',
                    activo=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                return 'Admin creado OK — email: admin@primar.cl / clave: Admin123!'
            else:
                admin.set_password('Admin123!')
                db.session.commit()
                return 'Contrasena reseteada OK — email: admin@primar.cl / clave: Admin123!'
        except Exception as e:
            return f'Error: {str(e)}'

    # ─────────────────────────────────────────────────────────
    # Ruta principal
    # ─────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # ─────────────────────────────────────────────────────────
    # Comandos CLI
    # ─────────────────────────────────────────────────────────
    @app.cli.command()
    def init_db():
        """Inicializa la base de datos."""
        db.create_all()
        print('✓ Base de datos inicializada correctamente')

    @app.cli.command()
    def create_admin():
        """Crea un usuario administrador."""
        admin = User.query.filter_by(email='admin@primar.cl').first()
        if admin:
            print('El usuario admin ya existe')
            return
        admin = User(
            nombre='Administrador',
            email='admin@primar.cl',
            rol='admin',
            activo=True
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin creado — email: admin@primar.cl / clave: Admin123!')

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )