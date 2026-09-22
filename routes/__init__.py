from .auth import auth_bp
from .dashboard import dashboard_bp
from .rendiciones import rendiciones_bp
from .aprobaciones import aprobaciones_bp
from .usuarios import usuarios_bp
from .reportes import reportes_bp
from .notificaciones import notificaciones_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'rendiciones_bp',
    'aprobaciones_bp',
    'usuarios_bp',
    'reportes_bp',
    'notificaciones_bp'
]