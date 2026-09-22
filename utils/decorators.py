from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """Decorador que requiere que el usuario sea administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('No tienes permisos para acceder a esta sección', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def permission_required(rol):
    """Decorador que requiere un rol específico o superior"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder', 'warning')
                return redirect(url_for('auth.login'))
            
            # Admin tiene acceso a todo
            if current_user.is_admin():
                return f(*args, **kwargs)
            
            # Verificar rol específico
            if rol == 'aprobador' and not current_user.can_approve():
                flash('No tienes permisos para acceder a esta sección', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_rendicion_ownership(f):
    """Decorador que verifica que el usuario sea dueño de la rendición o admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models import Rendicion
        
        rendicion_id = kwargs.get('id')
        if not rendicion_id:
            abort(404)
        
        rendicion = Rendicion.query.get_or_404(rendicion_id)
        
        if not current_user.is_admin() and rendicion.usuario_id != current_user.id:
            flash('No tienes permiso para acceder a esta rendición', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(roles):
    """
    Decorador para requerir roles específicos
    
    Args:
        roles: Lista de roles permitidos, ej: ['admin', 'aprobador']
    
    Uso:
        @role_required(['admin', 'aprobador'])
        def vista_para_admin_y_aprobador():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.rol not in roles:
                flash('No tienes permiso para acceder a esta página', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator