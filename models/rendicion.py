from datetime import datetime
from . import db

class Rendicion(db.Model):
    """Modelo de Rendición de Gastos"""
    __tablename__ = 'rendiciones'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_rendicion = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Usuario que crea la rendición
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    
    # Información de la rendiciónpython app.py

    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    proyecto = db.Column(db.String(100), nullable=True)
    centro_costo = db.Column(db.String(100), nullable=True)
    
    # Estados: pendiente, en_revision, aprobada, rechazada, pagada
    estado = db.Column(db.Enum('pendiente', 'en_revision', 'aprobada', 'rechazada', 'pagada',
                               name='estado_rendicion_enum'), 
                      default='pendiente', nullable=False, index=True)
    
    # Montos
    monto_total = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    monto_aprobado = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Aprobación
    aprobador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), 
                            nullable=True, index=True)
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)
    comentarios_aprobador = db.Column(db.Text, nullable=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, 
                                    onupdate=datetime.utcnow, nullable=False)
    fecha_envio = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    usuario = db.relationship('User', foreign_keys=[usuario_id], 
                             back_populates='rendiciones')
    aprobador = db.relationship('User', foreign_keys=[aprobador_id], 
                               back_populates='rendiciones_aprobadas')
    items = db.relationship('ItemRendicion', back_populates='rendicion', 
                           cascade='all, delete-orphan', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Rendicion, self).__init__(**kwargs)
        if not self.numero_rendicion:
            self.numero_rendicion = self.generar_numero_rendicion()
    
    @staticmethod
    def generar_numero_rendicion():
        """Genera un número de rendición único"""
        from datetime import datetime
        fecha = datetime.now()
        # Formato: REND-YYYYMMDD-XXXXX
        ultima = Rendicion.query.filter(
            Rendicion.numero_rendicion.like(f'REND-{fecha.strftime("%Y%m%d")}-%')
        ).order_by(Rendicion.id.desc()).first()
        
        if ultima:
            ultimo_numero = int(ultima.numero_rendicion.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f'REND-{fecha.strftime("%Y%m%d")}-{nuevo_numero:05d}'
    
    def calcular_monto_total(self):
        """Calcula el monto total sumando los items"""
        total = sum(item.monto for item in self.items.all())
        self.monto_total = total
        return total
    
    def puede_editar(self, user):
        """Verifica si el usuario puede editar la rendición"""
        if user.is_admin():
            return True
        if self.usuario_id == user.id and self.estado == 'pendiente':
            return True
        return False
    
    def puede_eliminar(self, user):
        """Verifica si el usuario puede eliminar la rendición"""
        if user.is_admin():
            return True
        if self.usuario_id == user.id and self.estado == 'pendiente':
            return True
        return False
    
    def puede_enviar(self, user):
        """Verifica si el usuario puede enviar la rendición a revisión"""
        return (self.usuario_id == user.id and 
                self.estado == 'pendiente' and 
                self.items.count() > 0)
    
    def puede_aprobar(self, user):
        """Verifica si el usuario puede aprobar la rendición"""
        return (user.can_approve() and 
                self.estado == 'en_revision' and 
                self.usuario_id != user.id)
    
    def enviar_a_revision(self):
        """Cambia el estado a 'en_revision'"""
        self.estado = 'en_revision'
        self.fecha_envio = datetime.utcnow()
    
    def aprobar(self, aprobador, comentarios=None):
        """Aprueba la rendición"""
        self.estado = 'aprobada'
        self.aprobador_id = aprobador.id
        self.fecha_aprobacion = datetime.utcnow()
        self.comentarios_aprobador = comentarios
        self.monto_aprobado = self.monto_total
    
    def rechazar(self, aprobador, comentarios):
        """Rechaza la rendición"""
        self.estado = 'rechazada'
        self.aprobador_id = aprobador.id
        self.fecha_aprobacion = datetime.utcnow()
        self.comentarios_aprobador = comentarios
    
    def get_estado_display(self):
        """Obtiene el nombre legible del estado"""
        estados = {
            'pendiente': 'Pendiente',
            'en_revision': 'En Revisión',
            'aprobada': 'Aprobada',
            'rechazada': 'Rechazada',
            'pagada': 'Pagada'
        }
        return estados.get(self.estado, self.estado)
    
    def get_estado_class(self):
        """Obtiene la clase CSS para el badge del estado"""
        clases = {
            'pendiente': 'warning',
            'en_revision': 'info',
            'aprobada': 'success',
            'rechazada': 'danger',
            'pagada': 'primary'
        }
        return clases.get(self.estado, 'secondary')
    
    def __repr__(self):
        return f'<Rendicion {self.numero_rendicion}>'
    
    def to_dict(self):
        """Convierte la rendición a diccionario"""
        return {
            'id': self.id,
            'numero_rendicion': self.numero_rendicion,
            'usuario': self.usuario.nombre if self.usuario else None,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'monto_total': float(self.monto_total) if self.monto_total else 0,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'aprobador': self.aprobador.nombre if self.aprobador else None,
            'fecha_aprobacion': self.fecha_aprobacion.isoformat() if self.fecha_aprobacion else None,
            'items_count': self.items.count()
        }