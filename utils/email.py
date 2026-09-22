from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def send_async_email(app, msg):
    """Enviar email de forma asíncrona"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f'Error al enviar email: {str(e)}')


def send_email(to, subject, template, **kwargs):
    """
    Enviar email
    
    Args:
        to: Email destinatario
        subject: Asunto del email
        template: Ruta al template HTML
        **kwargs: Variables para el template
    """
    app = current_app._get_current_object()
    
    msg = Message(
        subject=subject,
        recipients=[to] if isinstance(to, str) else to,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        msg.html = render_template(template, **kwargs)
        
        # Enviar de forma asíncrona
        thread = Thread(target=send_async_email, args=(app, msg))
        thread.start()
        
        return True
    except Exception as e:
        app.logger.error(f'Error preparando email: {str(e)}')
        return False


def send_password_reset_email(user, token):
    """Enviar email de recuperación de contraseña"""
    from flask import url_for
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    return send_email(
        to=user.email,
        subject='Recuperación de contraseña - Sistema Rendiciones',
        template='emails/reset_password.html',
        user=user,
        reset_url=reset_url
    )


def send_rendicion_notification(rendicion, tipo):
    """
    Enviar notificación por email sobre rendición
    
    Args:
        rendicion: Objeto Rendicion
        tipo: 'nueva', 'aprobada', 'rechazada'
    """
    if tipo == 'nueva':
        # Enviar a aprobadores
        from models import User
        aprobadores = User.query.filter(
            User.rol.in_(['admin', 'aprobador']),
            User.activo == True
        ).all()
        
        for aprobador in aprobadores:
            send_email(
                to=aprobador.email,
                subject=f'Nueva Rendición para Revisar - {rendicion.numero_rendicion}',
                template='emails/nueva_rendicion.html',
                aprobador=aprobador,
                rendicion=rendicion
            )
    
    elif tipo == 'aprobada':
        # Enviar al usuario
        send_email(
            to=rendicion.usuario.email,
            subject=f'Rendición Aprobada - {rendicion.numero_rendicion}',
            template='emails/rendicion_aprobada.html',
            user=rendicion.usuario,
            rendicion=rendicion
        )
    
    elif tipo == 'rechazada':
        # Enviar al usuario
        send_email(
            to=rendicion.usuario.email,
            subject=f'Rendición Rechazada - {rendicion.numero_rendicion}',
            template='emails/rendicion_rechazada.html',
            user=rendicion.usuario,
            rendicion=rendicion
        )