from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Rendicion, Notificacion
from utils.decorators import permission_required

aprobaciones_bp = Blueprint('aprobaciones', __name__, url_prefix='/aprobaciones')


@aprobaciones_bp.route('/')
@login_required
@permission_required('aprobador')
def index():
    """Lista de rendiciones pendientes de aprobación"""
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'en_revision')
    
    query = Rendicion.query
    
    # Filtrar por estado
    if estado:
        query = query.filter_by(estado=estado)
    
    # Ordenar por fecha de envío
    query = query.order_by(Rendicion.fecha_envio.desc())
    
    # Paginar
    from flask import current_app
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('aprobaciones/index.html',
                         rendiciones=pagination.items,
                         pagination=pagination,
                         estado=estado)


@aprobaciones_bp.route('/<int:id>/revisar')
@login_required
@permission_required('aprobador')
def revisar(id):
    """Revisar rendición para aprobar/rechazar"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_aprobar(current_user):
        flash('Esta rendición no está disponible para aprobación', 'error')
        return redirect(url_for('aprobaciones.index'))
    
    items = rendicion.items.all()
    
    return render_template('aprobaciones/revisar.html',
                         rendicion=rendicion,
                         items=items)


@aprobaciones_bp.route('/<int:id>/aprobar', methods=['POST'])
@login_required
@permission_required('aprobador')
def aprobar(id):
    """Aprobar rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_aprobar(current_user):
        flash('No puedes aprobar esta rendición', 'error')
        return redirect(url_for('aprobaciones.index'))
    
    comentarios = request.form.get('comentarios', '').strip()
    
    try:
        rendicion.aprobar(current_user, comentarios)
        db.session.commit()
        
        # Crear notificación para el usuario
        Notificacion.notificar_rendicion_aprobada(rendicion)
        db.session.commit()
        
        flash(f'Rendición {rendicion.numero_rendicion} aprobada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al aprobar la rendición: {str(e)}', 'error')
    
    return redirect(url_for('aprobaciones.index'))


@aprobaciones_bp.route('/<int:id>/rechazar', methods=['POST'])
@login_required
@permission_required('aprobador')
def rechazar(id):
    """Rechazar rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_aprobar(current_user):
        flash('No puedes rechazar esta rendición', 'error')
        return redirect(url_for('aprobaciones.index'))
    
    comentarios = request.form.get('comentarios', '').strip()
    
    if not comentarios:
        flash('Debes indicar el motivo del rechazo', 'error')
        return redirect(url_for('aprobaciones.revisar', id=id))
    
    try:
        rendicion.rechazar(current_user, comentarios)
        db.session.commit()
        
        # Crear notificación para el usuario
        Notificacion.notificar_rendicion_rechazada(rendicion)
        db.session.commit()
        
        flash(f'Rendición {rendicion.numero_rendicion} rechazada', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al rechazar la rendición: {str(e)}', 'error')
    
    return redirect(url_for('aprobaciones.index'))


@aprobaciones_bp.route('/historial')
@login_required
@permission_required('aprobador')
def historial():
    """Historial de aprobaciones del usuario actual"""
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado')
    
    query = Rendicion.query.filter_by(aprobador_id=current_user.id)
    
    # Filtrar por estado
    if estado and estado in ['aprobada', 'rechazada']:
        query = query.filter_by(estado=estado)
    else:
        query = query.filter(Rendicion.estado.in_(['aprobada', 'rechazada']))
    
    # Ordenar por fecha de aprobación
    query = query.order_by(Rendicion.fecha_aprobacion.desc())
    
    # Paginar
    from flask import current_app
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('aprobaciones/historial.html',
                         rendiciones=pagination.items,
                         pagination=pagination,
                         estado=estado)