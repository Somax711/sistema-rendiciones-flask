from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Notificacion

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')


@notificaciones_bp.route('/')
@login_required
def index():
    """Lista de notificaciones del usuario"""
    page = request.args.get('page', 1, type=int)
    
    query = current_user.notificaciones.order_by(
        Notificacion.fecha_creacion.desc()
    )
    
    from flask import current_app
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('notificaciones/index.html',
                         notificaciones=pagination.items,
                         pagination=pagination)


@notificaciones_bp.route('/api/list')
@login_required
def api_list():
    """API para obtener notificaciones (para dropdown)"""
    # Obtener últimas 10 notificaciones no leídas
    notificaciones = current_user.notificaciones.filter_by(leida=False).order_by(
        Notificacion.fecha_creacion.desc()
    ).limit(10).all()
    
    return jsonify({
        'notificaciones': [n.to_dict() for n in notificaciones],
        'total_no_leidas': current_user.get_notificaciones_no_leidas()
    })


@notificaciones_bp.route('/<int:id>/marcar-leida', methods=['POST'])
@login_required
def marcar_leida(id):
    """Marcar notificación como leída"""
    notificacion = Notificacion.query.get_or_404(id)
    
    # Verificar que la notificación pertenezca al usuario
    if notificacion.usuario_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    notificacion.marcar_leida()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'total_no_leidas': current_user.get_notificaciones_no_leidas()
    })


@notificaciones_bp.route('/marcar-todas-leidas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    """Marcar todas las notificaciones como leídas"""
    notificaciones = current_user.notificaciones.filter_by(leida=False).all()
    
    for notificacion in notificaciones:
        notificacion.marcar_leida()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'total_no_leidas': 0
    })


@notificaciones_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar notificación"""
    notificacion = Notificacion.query.get_or_404(id)
    
    if notificacion.usuario_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    db.session.delete(notificacion)
    db.session.commit()
    
    return jsonify({'success': True})