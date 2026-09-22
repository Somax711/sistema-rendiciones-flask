from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
from . import db

class User(UserMixin, db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'aprobador', 'usuario', name='rol_enum'), 
                    nullable=False, default='usuario')
    
    # Estado y seguridad
    activo = db.Column(db.Boolean, default=True, nullable=False)
    email_verificado = db.Column(db.Boolean, default=False, nullable=False)
    
    # MFA 
    mfa_habilitado = db.Column(db.Boolean, default=False, nullable=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    
    # Recuperación de contraseña
    token_recuperacion = db.Column(db.String(100), nullable=True)
    token_recuperacion_expira = db.Column(db.DateTime, nullable=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, 
                                    onupdate=datetime.utcnow, nullable=False)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    
    # Información adicional
    telefono = db.Column(db.String(20), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    cargo = db.Column(db.String(100), nullable=True)
  
    # Relaciones
    rendiciones = db.relationship('Rendicion', 
                             foreign_keys='Rendicion.usuario_id',
                             back_populates='usuario', 
                             cascade='all, delete-orphan', 
                             lazy='dynamic')
    rendiciones_aprobadas = db.relationship('Rendicion', 
                                       foreign_keys='Rendicion.aprobador_id',
                                       back_populates='aprobador', 
                                       lazy='dynamic')
    notificaciones = db.relationship('Notificacion', 
                                back_populates='usuario',
                                cascade='all, delete-orphan', 
                                lazy='dynamic')
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def generate_mfa_secret(self):
        """Genera un secreto para MFA"""
        self.mfa_secret = pyotp.random_base32()
        return self.mfa_secret
    
    def get_mfa_uri(self):
        """Obtiene la URI para generar QR de MFA"""
        if not self.mfa_secret:
            self.generate_mfa_secret()
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email,
            issuer_name='Sistema Rendiciones Primar'
        )
    
    def verify_mfa_token(self, token):
        """Verifica un token MFA"""
        if not self.mfa_secret:
            return False
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == 'admin'
    
    def is_aprobador(self):
        """Verifica si el usuario es aprobador"""
        return self.rol == 'aprobador'
    
    def can_approve(self):
        """Verifica si el usuario puede aprobar rendiciones"""
        return self.rol in ['admin', 'aprobador']
    
    def get_notificaciones_no_leidas(self):
        """Obtiene el conteo de notificaciones no leídas"""
        return Notificacion.query.filter_by(
            usuario_id=self.id,
            leida=False
        ).count()
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'departamento': self.departamento,
            'cargo': self.cargo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }