from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User
from utils.decorators import admin_required

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuarios_bp.route('/')
@login_required
@admin_required
def index():
    """Lista de usuarios"""
    page = request.args.get('page', 1, type=int)
    rol = request.args.get('rol')
    activo = request.args.get('activo')
    buscar = request.args.get('buscar')
    
    query = User.query
    
    # Filtros
    if rol and rol in ['admin', 'aprobador', 'usuario']:
        query = query.filter_by(rol=rol)
    
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        query = query.filter_by(activo=activo_bool)
    
    if buscar:
        query = query.filter(
            db.or_(
                User.nombre.like(f'%{buscar}%'),
                User.email.like(f'%{buscar}%'),
                User.departamento.like(f'%{buscar}%')
            )
        )
    
    # Ordenar
    query = query.order_by(User.fecha_creacion.desc())
    
    # Paginar
    from flask import current_app
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('usuarios/index.html',
                         usuarios=pagination.items,
                         pagination=pagination,
                         rol=rol,
                         activo=activo,
                         buscar=buscar)


@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            rol = request.form.get('rol', 'usuario')
            telefono = request.form.get('telefono', '').strip()
            departamento = request.form.get('departamento', '').strip()
            cargo = request.form.get('cargo', '').strip()
            
            # Validaciones
            if not all([nombre, email, password]):
                flash('Nombre, email y contraseña son obligatorios', 'error')
                return redirect(url_for('usuarios.crear'))
            
            if len(password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'error')
                return redirect(url_for('usuarios.crear'))
            
            if User.query.filter_by(email=email).first():
                flash('Ya existe un usuario con ese email', 'error')
                return redirect(url_for('usuarios.crear'))
            
            # Crear usuario
            usuario = User(
                nombre=nombre,
                email=email,
                rol=rol,
                telefono=telefono,
                departamento=departamento,
                cargo=cargo,
                activo=True,
                email_verificado=True
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Usuario {nombre} creado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('usuarios/crear.html')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    """Editar usuario"""
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nombre = request.form.get('nombre', usuario.nombre).strip()
            email = request.form.get('email', usuario.email).strip().lower()
            usuario.rol = request.form.get('rol', usuario.rol)
            usuario.telefono = request.form.get('telefono', '').strip()
            usuario.departamento = request.form.get('departamento', '').strip()
            usuario.cargo = request.form.get('cargo', '').strip()
            
            # Verificar si el email ya existe (excepto el actual)
            if email != usuario.email:
                if User.query.filter_by(email=email).first():
                    flash('Ya existe un usuario con ese email', 'error')
                    return redirect(url_for('usuarios.editar', id=id))
                usuario.email = email
            
            # Cambiar contraseña si se proporcionó
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                if len(new_password) < 8:
                    flash('La contraseña debe tener al menos 8 caracteres', 'error')
                    return redirect(url_for('usuarios.editar', id=id))
                usuario.set_password(new_password)
            
            db.session.commit()
            
            flash(f'Usuario {usuario.nombre} actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
    
    return render_template('usuarios/editar.html', usuario=usuario)


@usuarios_bp.route('/<int:id>/toggle-estado', methods=['POST'])
@login_required
@admin_required
def toggle_estado(id):
    """Activar/Desactivar usuario"""
    usuario = User.query.get_or_404(id)
    
    # No permitir desactivar al propio usuario
    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'error')
        return redirect(url_for('usuarios.index'))
    
    try:
        usuario.activo = not usuario.activo
        db.session.commit()
        
        estado = 'activado' if usuario.activo else 'desactivado'
        flash(f'Usuario {usuario.nombre} {estado} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado: {str(e)}', 'error')
    
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar(id):
    """Eliminar usuario"""
    usuario = User.query.get_or_404(id)
    
    # No permitir eliminar al propio usuario
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'error')
        return redirect(url_for('usuarios.index'))
    
    try:
        nombre = usuario.nombre
        db.session.delete(usuario)
        db.session.commit()
        
        flash(f'Usuario {nombre} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/<int:id>')
@login_required
@admin_required
def detalle(id):
    """Ver detalle de usuario"""
    usuario = User.query.get_or_404(id)
    
    # Estadísticas del usuario
    total_rendiciones = usuario.rendiciones.count()
    rendiciones_aprobadas = usuario.rendiciones.filter_by(estado='aprobada').count()
    rendiciones_rechazadas = usuario.rendiciones.filter_by(estado='rechazada').count()
    rendiciones_pendientes = usuario.rendiciones.filter_by(estado='pendiente').count()
    
    # Monto total de rendiciones aprobadas
    from sqlalchemy import func
    from models import Rendicion
    
    monto_total = db.session.query(
        func.sum(Rendicion.monto_aprobado)
    ).filter(
        Rendicion.usuario_id == usuario.id,
        Rendicion.estado.in_(['aprobada', 'pagada'])
    ).scalar() or 0
    
    # Rendiciones recientes
    rendiciones_recientes = usuario.rendiciones.order_by(
        Rendicion.fecha_creacion.desc()
    ).limit(10).all()
    
    stats = {
        'total_rendiciones': total_rendiciones,
        'aprobadas': rendiciones_aprobadas,
        'rechazadas': rendiciones_rechazadas,
        'pendientes': rendiciones_pendientes,
        'monto_total': float(monto_total)
    }
    
    return render_template('usuarios/detalle.html',
                         usuario=usuario,
                         stats=stats,
                         rendiciones_recientes=rendiciones_recientes)


@usuarios_bp.route('/api/check-email')
@login_required
@admin_required
def check_email():
    """API para verificar si un email ya existe"""
    email = request.args.get('email', '').strip().lower()
    user_id = request.args.get('user_id', type=int)
    
    query = User.query.filter_by(email=email)
    
    # Si es una edición, excluir el usuario actual
    if user_id:
        query = query.filter(User.id != user_id)
    
    existe = query.first() is not None
    
    return jsonify({'existe': existe})