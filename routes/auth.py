from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
import secrets
from models import db, User
from utils.email import send_email
import pyotp
import qrcode
import io
import base64


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Email o contraseña incorrectos', 'error')
            return render_template('auth/login.html')
        
        if not user.activo:
            flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'error')
            return render_template('auth/login.html')
        
        if user.mfa_habilitado:
            session['mfa_user_id'] = user.id
            session['mfa_remember'] = remember
            return redirect(url_for('auth.verify_mfa'))
        
        # Login exitoso
        login_user(user, remember=remember)
        user.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        flash(f'¡Bienvenido {user.nombre}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')


@auth_bp.route('/verify-mfa', methods=['GET', 'POST'])
def verify_mfa():
    """Verificación de MFA"""
    user_id = session.get('mfa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        session.pop('mfa_user_id', None)
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        
        if not token:
            flash('Por favor ingresa el código de verificación', 'error')
            return render_template('auth/mfa.html')
        
        if user.verify_mfa_token(token):
            remember = session.get('mfa_remember', False)
            login_user(user, remember=remember)
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            # Limpiar sesión MFA
            session.pop('mfa_user_id', None)
            session.pop('mfa_remember', None)
            
            flash(f'¡Bienvenido {user.nombre}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Código de verificación incorrecto', 'error')
    
    return render_template('auth/mfa.html', user=user)


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar_password():
    """Recuperación de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Por favor ingresa tu email', 'error')
            return render_template('auth/recuperar.html')
        
        user = User.query.filter_by(email=email).first()
        
        flash('Si el email existe, recibirás un enlace para recuperar tu contraseña', 'info')
        
        if user and user.activo:
            token = secrets.token_urlsafe(32)
            user.token_recuperacion = token
            user.token_recuperacion_expira = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Enviar email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(
                to=user.email,
                subject='Recuperación de contraseña - Sistema Rendiciones',
                template='emails/reset_password.html',
                user=user,
                reset_url=reset_url
            )
        
        return render_template('auth/recuperar_enviado.html')
    
    return render_template('auth/recuperar.html')


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Restablecer contraseña con token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    user = User.query.filter_by(token_recuperacion=token).first()
    
    if not user or not user.token_recuperacion_expira:
        flash('El enlace de recuperación no es válido', 'error')
        return redirect(url_for('auth.login'))
    
    if datetime.utcnow() > user.token_recuperacion_expira:
        flash('El enlace de recuperación ha expirado', 'error')
        return redirect(url_for('auth.recuperar_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not password or not password_confirm:
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        # Actualizar contraseña
        user.set_password(password)
        user.token_recuperacion = None
        user.token_recuperacion_expira = None
        db.session.commit()
        
        flash('Tu contraseña ha sido actualizada exitosamente', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Perfil de usuario"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            current_user.nombre = request.form.get('nombre', current_user.nombre)
            current_user.telefono = request.form.get('telefono', current_user.telefono)
            current_user.departamento = request.form.get('departamento', current_user.departamento)
            current_user.cargo = request.form.get('cargo', current_user.cargo)
            
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('La contraseña actual es incorrecta', 'error')
            elif new_password != confirm_password:
                flash('Las contraseñas nuevas no coinciden', 'error')
            elif len(new_password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Contraseña actualizada exitosamente', 'success')
        
        elif action == 'enable_mfa':
            if not current_user.mfa_secret:
                current_user.generate_mfa_secret()
                db.session.commit()
            
            # Generar QR
            uri = current_user.get_mfa_uri()
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return render_template('auth/perfil.html', 
                                 user=current_user, 
                                 qr_code=qr_base64,
                                 mfa_secret=current_user.mfa_secret)
        
        elif action == 'verify_mfa':
            token = request.form.get('mfa_token')
            if current_user.verify_mfa_token(token):
                current_user.mfa_habilitado = True
                db.session.commit()
                flash('Autenticación de dos factores habilitada exitosamente', 'success')
            else:
                flash('Código de verificación incorrecto', 'error')
                return redirect(url_for('auth.perfil'))
        
        elif action == 'disable_mfa':
            current_user.mfa_habilitado = False
            db.session.commit()
            flash('Autenticación de dos factores deshabilitada', 'info')
        
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/perfil.html', user=current_user)