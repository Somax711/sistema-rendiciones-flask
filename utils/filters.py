from datetime import datetime
import locale


def register_filters(app):
    """Registrar filtros personalizados para Jinja2"""
    
    @app.template_filter('format_currency')
    def format_currency(value):
        """Formatear número como moneda chilena"""
        try:
            return f"${value:,.0f}".replace(',', '.')
        except (ValueError, TypeError):
            return "$0"
    
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        """Formatear fecha"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('format_datetime')
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        """Formatear fecha y hora"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('time_ago')
    def time_ago(value):
        """Mostrar tiempo transcurrido (ej: hace 2 horas)"""
        if value is None:
            return ''
        
        now = datetime.utcnow()
        diff = now - value
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'hace unos segundos'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'hace {minutes} minuto{"s" if minutes > 1 else ""}'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'hace {hours} hora{"s" if hours > 1 else ""}'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'hace {days} día{"s" if days > 1 else ""}'
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f'hace {weeks} semana{"s" if weeks > 1 else ""}'
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f'hace {months} mes{"es" if months > 1 else ""}'
        else:
            years = int(seconds / 31536000)
            return f'hace {years} año{"s" if years > 1 else ""}'
    
    @app.template_filter('truncate_text')
    def truncate_text(value, length=50):
        """Truncar texto a longitud específica"""
        if value is None:
            return ''
        if len(value) <= length:
            return value
        return value[:length] + '...'
    
    @app.template_filter('file_size')
    def file_size(value):
        """Formatear tamaño de archivo"""
        try:
            value = int(value)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if value < 1024.0:
                    return f"{value:.1f} {unit}"
                value /= 1024.0
            return f"{value:.1f} TB"
        except (ValueError, TypeError):
            return "0 B"
    
    @app.template_filter('estado_badge_class')
    def estado_badge_class(estado):
        """Obtener clase CSS para badge de estado"""
        clases = {
            'pendiente': 'warning',
            'en_revision': 'info',
            'aprobada': 'success',
            'rechazada': 'danger',
            'pagada': 'primary'
        }
        return clases.get(estado, 'secondary')
    
    @app.template_filter('rol_badge_class')
    def rol_badge_class(rol):
        """Obtener clase CSS para badge de rol"""
        clases = {
            'admin': 'danger',
            'aprobador': 'primary',
            'usuario': 'secondary'
        }
        return clases.get(rol, 'secondary')
    
    @app.template_filter('rol_display')
    def rol_display(rol):
        """Obtener nombre legible del rol"""
        roles = {
            'admin': 'Administrador',
            'aprobador': 'Aprobador',
            'usuario': 'Usuario'
        }
        return roles.get(rol, rol)