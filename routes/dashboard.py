from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from models import db, Rendicion, User, ItemRendicion

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal según rol del usuario"""
    if current_user.is_admin():
        return render_template('dashboard/admin.html', stats=get_admin_stats())
    elif current_user.is_aprobador():
        return render_template('dashboard/aprobador.html', stats=get_aprobador_stats())
    else:
        return render_template('dashboard/usuario.html', stats=get_usuario_stats())


def get_admin_stats():
    """Estadísticas para el dashboard de admin"""
    # Contadores generales
    total_usuarios = User.query.filter_by(activo=True).count()
    total_rendiciones = Rendicion.query.count()
    rendiciones_pendientes = Rendicion.query.filter_by(estado='en_revision').count()
    rendiciones_mes = Rendicion.query.filter(
        extract('month', Rendicion.fecha_creacion) == datetime.now().month,
        extract('year', Rendicion.fecha_creacion) == datetime.now().year
    ).count()
    
    # Montos
    monto_total = db.session.query(
        func.sum(Rendicion.monto_total)
    ).filter(Rendicion.estado.in_(['aprobada', 'pagada'])).scalar() or 0
    
    monto_pendiente = db.session.query(
        func.sum(Rendicion.monto_total)
    ).filter_by(estado='en_revision').scalar() or 0
    
    monto_mes = db.session.query(
        func.sum(Rendicion.monto_total)
    ).filter(
        extract('month', Rendicion.fecha_creacion) == datetime.now().month,
        extract('year', Rendicion.fecha_creacion) == datetime.now().year,
        Rendicion.estado.in_(['aprobada', 'pagada'])
    ).scalar() or 0
    
    # Rendiciones por estado
    rendiciones_por_estado = db.session.query(
        Rendicion.estado,
        func.count(Rendicion.id)
    ).group_by(Rendicion.estado).all()
    
    estados_dict = {estado: count for estado, count in rendiciones_por_estado}
    
    # Rendiciones recientes
    rendiciones_recientes = Rendicion.query.order_by(
        Rendicion.fecha_creacion.desc()
    ).limit(10).all()
    
    # Top usuarios por monto
    top_usuarios = db.session.query(
        User.nombre,
        func.sum(Rendicion.monto_total).label('total')
    ).join(Rendicion).filter(
        Rendicion.estado.in_(['aprobada', 'pagada'])
    ).group_by(User.id).order_by(func.sum(Rendicion.monto_total).desc()).limit(5).all()
    
    # Rendiciones por mes (últimos 6 meses)
    rendiciones_por_mes = []
    for i in range(5, -1, -1):
        fecha = datetime.now() - timedelta(days=30*i)
        count = Rendicion.query.filter(
            extract('month', Rendicion.fecha_creacion) == fecha.month,
            extract('year', Rendicion.fecha_creacion) == fecha.year
        ).count()
        rendiciones_por_mes.append({
            'mes': fecha.strftime('%B'),
            'count': count
        })
    
    return {
        'total_usuarios': total_usuarios,
        'total_rendiciones': total_rendiciones,
        'rendiciones_pendientes': rendiciones_pendientes,
        'rendiciones_mes': rendiciones_mes,
        'monto_total': float(monto_total),
        'monto_pendiente': float(monto_pendiente),
        'monto_mes': float(monto_mes),
        'estados': estados_dict,
        'rendiciones_recientes': rendiciones_recientes,
        'top_usuarios': top_usuarios,
        'rendiciones_por_mes': rendiciones_por_mes
    }


def get_aprobador_stats():
    """Estadísticas para el dashboard de aprobador"""
    # Rendiciones pendientes de aprobar
    pendientes = Rendicion.query.filter_by(estado='en_revision').count()
    
    # Rendiciones que he aprobado
    aprobadas = Rendicion.query.filter_by(
        aprobador_id=current_user.id,
        estado='aprobada'
    ).count()
    
    # Rendiciones aprobadas este mes
    aprobadas_mes = Rendicion.query.filter(
        Rendicion.aprobador_id == current_user.id,
        Rendicion.estado == 'aprobada',
        extract('month', Rendicion.fecha_aprobacion) == datetime.now().month,
        extract('year', Rendicion.fecha_aprobacion) == datetime.now().year
    ).count()
    
    # Monto total aprobado
    monto_aprobado = db.session.query(
        func.sum(Rendicion.monto_aprobado)
    ).filter(
        Rendicion.aprobador_id == current_user.id,
        Rendicion.estado.in_(['aprobada', 'pagada'])
    ).scalar() or 0
    
    # Rendiciones pendientes de revisión
    rendiciones_pendientes = Rendicion.query.filter_by(
        estado='en_revision'
    ).order_by(Rendicion.fecha_envio.asc()).limit(10).all()
    
    # Mis aprobaciones recientes
    mis_aprobaciones = Rendicion.query.filter(
        Rendicion.aprobador_id == current_user.id,
        Rendicion.estado.in_(['aprobada', 'rechazada'])
    ).order_by(Rendicion.fecha_aprobacion.desc()).limit(10).all()
    
    return {
        'pendientes': pendientes,
        'aprobadas': aprobadas,
        'aprobadas_mes': aprobadas_mes,
        'monto_aprobado': float(monto_aprobado),
        'rendiciones_pendientes': rendiciones_pendientes,
        'mis_aprobaciones': mis_aprobaciones
    }


def get_usuario_stats():
    """Estadísticas para el dashboard de usuario"""
    # Mis rendiciones
    total_rendiciones = current_user.rendiciones.count()
    pendientes = current_user.rendiciones.filter_by(estado='pendiente').count()
    en_revision = current_user.rendiciones.filter_by(estado='en_revision').count()
    aprobadas = current_user.rendiciones.filter_by(estado='aprobada').count()
    rechazadas = current_user.rendiciones.filter_by(estado='rechazada').count()
    
    # Monto total de rendiciones aprobadas
    monto_aprobado = db.session.query(
        func.sum(Rendicion.monto_aprobado)
    ).filter(
        Rendicion.usuario_id == current_user.id,
        Rendicion.estado.in_(['aprobada', 'pagada'])
    ).scalar() or 0
    
    # Monto pendiente
    monto_pendiente = db.session.query(
        func.sum(Rendicion.monto_total)
    ).filter(
        Rendicion.usuario_id == current_user.id,
        Rendicion.estado == 'en_revision'
    ).scalar() or 0
    
    # Rendiciones este mes
    rendiciones_mes = current_user.rendiciones.filter(
        extract('month', Rendicion.fecha_creacion) == datetime.now().month,
        extract('year', Rendicion.fecha_creacion) == datetime.now().year
    ).count()
    
    # Mis rendiciones recientes
    rendiciones_recientes = current_user.rendiciones.order_by(
        Rendicion.fecha_creacion.desc()
    ).limit(10).all()
    
    # Gastos por tipo (últimos 3 meses)
    tres_meses_atras = datetime.now() - timedelta(days=90)
    gastos_por_tipo = db.session.query(
        ItemRendicion.tipo_gasto,
        func.sum(ItemRendicion.monto).label('total')
    ).join(Rendicion).filter(
        Rendicion.usuario_id == current_user.id,
        Rendicion.fecha_creacion >= tres_meses_atras
    ).group_by(ItemRendicion.tipo_gasto).all()
    
    return {
        'total_rendiciones': total_rendiciones,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'monto_aprobado': float(monto_aprobado),
        'monto_pendiente': float(monto_pendiente),
        'rendiciones_mes': rendiciones_mes,
        'rendiciones_recientes': rendiciones_recientes,
        'gastos_por_tipo': gastos_por_tipo
    }