import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Rendicion, ItemRendicion, Notificacion
from utils.decorators import permission_required

rendiciones_bp = Blueprint('rendiciones', __name__, url_prefix='/rendiciones')


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@rendiciones_bp.route('/')
@login_required
def index():
    """Listar rendiciones"""
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado')
    buscar = request.args.get('buscar')
    
    query = Rendicion.query
    
    # Filtrar por usuario 
    if not current_user.can_approve():
        query = query.filter_by(usuario_id=current_user.id)
    
    # Filtrar por estado
    if estado and estado in ['pendiente', 'en_revision', 'aprobada', 'rechazada', 'pagada']:
        query = query.filter_by(estado=estado)
    
    # Búsqueda
    if buscar:
        query = query.filter(
            db.or_(
                Rendicion.numero_rendicion.like(f'%{buscar}%'),
                Rendicion.descripcion.like(f'%{buscar}%')
            )
        )
    
    # Ordenar
    query = query.order_by(Rendicion.fecha_creacion.desc())
    
    # Paginar
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('rendiciones/index.html', 
                         rendiciones=pagination.items,
                         pagination=pagination,
                         estado=estado,
                         buscar=buscar)


@rendiciones_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crear nueva rendición"""
    if request.method == 'POST':
        try:
            # Datos de la rendición
            fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date()
            descripcion = request.form.get('descripcion', '').strip()
            proyecto = request.form.get('proyecto', '').strip()
            centro_costo = request.form.get('centro_costo', '').strip()
            
            # Validaciones
            if fecha_inicio > fecha_fin:
                flash('La fecha de inicio no puede ser mayor a la fecha de fin', 'error')
                return redirect(url_for('rendiciones.crear'))
            
            # Crear rendición
            rendicion = Rendicion(
                usuario_id=current_user.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=descripcion,
                proyecto=proyecto,
                centro_costo=centro_costo
            )
            
            db.session.add(rendicion)
            db.session.flush()  # Para obtener el ID
            
            # Procesar items
            items_count = int(request.form.get('items_count', 0))
            
            for i in range(items_count):
                fecha_gasto = request.form.get(f'items[{i}][fecha_gasto]')
                tipo_gasto = request.form.get(f'items[{i}][tipo_gasto]')
                descripcion_item = request.form.get(f'items[{i}][descripcion]')
                monto = request.form.get(f'items[{i}][monto]')
                tipo_documento = request.form.get(f'items[{i}][tipo_documento]', 'boleta')
                numero_documento = request.form.get(f'items[{i}][numero_documento]', '')
                proveedor = request.form.get(f'items[{i}][proveedor]', '')
                
                if not all([fecha_gasto, tipo_gasto, descripcion_item, monto]):
                    continue
                
                # Crear item
                item = ItemRendicion(
                    rendicion_id=rendicion.id,
                    fecha_gasto=datetime.strptime(fecha_gasto, '%Y-%m-%d').date(),
                    tipo_gasto=tipo_gasto,
                    descripcion=descripcion_item,
                    monto=float(monto),
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento,
                    proveedor=proveedor
                )
                
                # Procesar archivo comprobante
                file_key = f'items[{i}][comprobante]'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Añadir timestamp para evitar duplicados
                        name, ext = os.path.splitext(filename)
                        filename = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                        
                        filepath = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            'comprobantes',
                            filename
                        )
                        file.save(filepath)
                        item.comprobante = filename
                        item.comprobante_original = file.filename
                
                db.session.add(item)
            
            # Calcular monto total
            rendicion.calcular_monto_total()
            
            db.session.commit()
            
            flash(f'Rendición {rendicion.numero_rendicion} creada exitosamente', 'success')
            return redirect(url_for('rendiciones.detalle', id=rendicion.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la rendición: {str(e)}', 'error')
            return redirect(url_for('rendiciones.crear'))
    
    return render_template('rendiciones/crear.html', tipos_gasto=ItemRendicion.TIPOS_GASTO)


@rendiciones_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de una rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.rol == 'usuario':
        if rendicion.usuario_id != current_user.id:
            flash('No tienes permiso para ver esta rendición', 'danger')
            abort(403)
    
    return render_template('rendiciones/ver.html', rendicion=rendicion)



@rendiciones_bp.route('/<int:id>/detalle')
@login_required
def detalle(id):
    """Ver detalle de rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.can_approve() and rendicion.usuario_id != current_user.id:
        flash('No tienes permiso para ver esta rendición', 'error')
        return redirect(url_for('rendiciones.index'))
    
    items = rendicion.items.all()
    
    return render_template('rendiciones/detalle.html', 
                         rendicion=rendicion, 
                         items=items)


@rendiciones_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    # Verificar permisos
    if not rendicion.puede_editar(current_user):
        flash('No tienes permiso para editar esta rendición', 'error')
        return redirect(url_for('rendiciones.index'))
    
    if request.method == 'POST':
        try:
            rendicion.fecha_inicio = datetime.strptime(
                request.form.get('fecha_inicio'), '%Y-%m-%d'
            ).date()
            rendicion.fecha_fin = datetime.strptime(
                request.form.get('fecha_fin'), '%Y-%m-%d'
            ).date()
            rendicion.descripcion = request.form.get('descripcion', '').strip()
            rendicion.proyecto = request.form.get('proyecto', '').strip()
            rendicion.centro_costo = request.form.get('centro_costo', '').strip()
            
            db.session.commit()
            
            flash('Rendición actualizada exitosamente', 'success')
            return redirect(url_for('rendiciones.detalle', id=rendicion.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la rendición: {str(e)}', 'error')
    
    return render_template('rendiciones/editar.html', rendicion=rendicion)


@rendiciones_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar rendición"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_eliminar(current_user):
        flash('No tienes permiso para eliminar esta rendición', 'error')
        return redirect(url_for('rendiciones.index'))
    
    try:
        # Eliminar archivos de comprobantes
        for item in rendicion.items.all():
            if item.comprobante:
                filepath = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'comprobantes',
                    item.comprobante
                )
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        numero = rendicion.numero_rendicion
        db.session.delete(rendicion)
        db.session.commit()
        
        flash(f'Rendición {numero} eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la rendición: {str(e)}', 'error')
    
    return redirect(url_for('rendiciones.index'))


@rendiciones_bp.route('/<int:id>/enviar', methods=['POST'])
@login_required
def enviar(id):
    """Enviar rendición a revisión"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_enviar(current_user):
        flash('No puedes enviar esta rendición a revisión', 'error')
        return redirect(url_for('rendiciones.detalle', id=id))
    
    try:
        rendicion.enviar_a_revision()
        db.session.commit()
        
        # Crear notificaciones para aprobadores
        Notificacion.notificar_nueva_rendicion(rendicion)
        db.session.commit()
        
        flash(f'Rendición {rendicion.numero_rendicion} enviada a revisión', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al enviar la rendición: {str(e)}', 'error')
    
    return redirect(url_for('rendiciones.detalle', id=id))


@rendiciones_bp.route('/comprobante/<filename>')
@login_required
def ver_comprobante(filename):
    """Ver archivo de comprobante"""
    filepath = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'comprobantes',
        filename
    )
    
    if not os.path.exists(filepath):
        flash('Comprobante no encontrado', 'error')
        return redirect(url_for('rendiciones.index'))
    
    return send_file(filepath)


@rendiciones_bp.route('/<int:id>/items/agregar', methods=['POST'])
@login_required
def agregar_item(id):
    """Agregar item a rendición existente"""
    rendicion = Rendicion.query.get_or_404(id)
    
    if not rendicion.puede_editar(current_user):
        return {'error': 'No tienes permiso'}, 403
    
    try:
        item = ItemRendicion(
            rendicion_id=rendicion.id,
            fecha_gasto=datetime.strptime(request.form.get('fecha_gasto'), '%Y-%m-%d').date(),
            tipo_gasto=request.form.get('tipo_gasto'),
            descripcion=request.form.get('descripcion'),
            monto=float(request.form.get('monto')),
            tipo_documento=request.form.get('tipo_documento', 'boleta'),
            numero_documento=request.form.get('numero_documento', ''),
            proveedor=request.form.get('proveedor', '')
        )
        
        # Procesar comprobante
        if 'comprobante' in request.files:
            file = request.files['comprobante']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                
                filepath = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'comprobantes',
                    filename
                )
                file.save(filepath)
                item.comprobante = filename
                item.comprobante_original = file.filename
        
        db.session.add(item)
        rendicion.calcular_monto_total()
        db.session.commit()
        
        flash('Item agregado exitosamente', 'success')
        return redirect(url_for('rendiciones.detalle', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar item: {str(e)}', 'error')
        return redirect(url_for('rendiciones.detalle', id=id))


@rendiciones_bp.route('/items/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_item(id):
    """Eliminar item de rendición"""
    item = ItemRendicion.query.get_or_404(id)
    rendicion = item.rendicion
    
    if not rendicion.puede_editar(current_user):
        return {'error': 'No tienes permiso'}, 403
    
    try:
        # Eliminar archivo
        if item.comprobante:
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'comprobantes',
                item.comprobante
            )
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(item)
        rendicion.calcular_monto_total()
        db.session.commit()
        
        flash('Item eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar item: {str(e)}', 'error')
    
    return redirect(url_for('rendiciones.detalle', id=rendicion.id))