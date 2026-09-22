from datetime import datetime
from . import db


class Notificacion(db.Model):
    """Modelo de Notificación"""
    __tablename__ = 'notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    
    # Contenido de la notificación
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.Enum('info', 'success', 'warning', 'error',
                            name='tipo_notificacion_enum'), 
                    default='info', nullable=False)
    
    # Referencia a rendición (opcional)
    rendicion_id = db.Column(db.Integer, db.ForeignKey('rendiciones.id', ondelete='CASCADE'), 
                            nullable=True, index=True)
    
    # Estado
    leida = db.Column(db.Boolean, default=False, nullable=False, index=True)
    fecha_lectura = db.Column(db.DateTime, nullable=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
     # Relaciones
    usuario = db.relationship('User', back_populates='notificaciones')
    rendicion = db.relationship('Rendicion')
    
    def marcar_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.utcnow()
    
    def get_icon(self):
        """Obtiene el ícono según el tipo"""
        iconos = {
            'info': 'bi-info-circle',
            'success': 'bi-check-circle',
            'warning': 'bi-exclamation-triangle',
            'error': 'bi-x-circle'
        }
        return iconos.get(self.tipo, 'bi-bell')
    
    def get_class(self):
        """Obtiene la clase CSS según el tipo"""
        clases = {
            'info': 'primary',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger'
        }
        return clases.get(self.tipo, 'secondary')
    
    @staticmethod
    def crear_notificacion(usuario_id, titulo, mensaje, tipo='info', rendicion_id=None):
        """Crea una nueva notificación"""
        notificacion = Notificacion(
            usuario_id=usuario_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            rendicion_id=rendicion_id
        )
        db.session.add(notificacion)
        return notificacion
    
    @staticmethod
    def notificar_nueva_rendicion(rendicion):
        """Notifica a los aprobadores sobre una nueva rendición"""
        from .user import User
        aprobadores = User.query.filter(
            User.rol.in_(['admin', 'aprobador']),
            User.activo == True
        ).all()
        
        for aprobador in aprobadores:
            Notificacion.crear_notificacion(
                usuario_id=aprobador.id,
                titulo='Nueva Rendición para Revisar',
                mensaje=f'La rendición {rendicion.numero_rendicion} de {rendicion.usuario.nombre} '
                       f'está pendiente de revisión. Monto: ${rendicion.monto_total:,.0f}',
                tipo='info',
                rendicion_id=rendicion.id
            )
    
    @staticmethod
    def notificar_rendicion_aprobada(rendicion):
        """Notifica al usuario que su rendición fue aprobada"""
        Notificacion.crear_notificacion(
            usuario_id=rendicion.usuario_id,
            titulo='Rendición Aprobada',
            mensaje=f'Tu rendición {rendicion.numero_rendicion} ha sido aprobada '
                   f'por {rendicion.aprobador.nombre}. '
                   f'Monto aprobado: ${rendicion.monto_aprobado:,.0f}',
            tipo='success',
            rendicion_id=rendicion.id
        )
    
    @staticmethod
    def notificar_rendicion_rechazada(rendicion):
        """Notifica al usuario que su rendición fue rechazada"""
        Notificacion.crear_notificacion(
            usuario_id=rendicion.usuario_id,
            titulo='Rendición Rechazada',
            mensaje=f'Tu rendición {rendicion.numero_rendicion} ha sido rechazada '
                   f'por {rendicion.aprobador.nombre}. '
                   f'Motivo: {rendicion.comentarios_aprobador or "Sin comentarios"}',
            tipo='warning',
            rendicion_id=rendicion.id
        )
    
    def __repr__(self):
        return f'<Notificacion {self.id} - {self.titulo[:30]}>'
    
    def to_dict(self):
        """Convierte la notificación a diccionario"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'tipo': self.tipo,
            'leida': self.leida,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_lectura': self.fecha_lectura.isoformat() if self.fecha_lectura else None,
            'rendicion_id': self.rendicion_id,
            'icon': self.get_icon(),
            'class': self.get_class()
        }