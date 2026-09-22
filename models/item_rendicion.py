from datetime import datetime
from . import db

class ItemRendicion(db.Model):
    """Modelo de Item de Rendición (gasto individual)"""
    __tablename__ = 'items_rendicion'
    
    id = db.Column(db.Integer, primary_key=True)
    rendicion_id = db.Column(db.Integer, db.ForeignKey('rendiciones.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    
    # Información del gasto
    fecha_gasto = db.Column(db.Date, nullable=False)
    tipo_gasto = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    proveedor = db.Column(db.String(200), nullable=True)
    
    # Montos
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    moneda = db.Column(db.String(3), default='CLP', nullable=False)
    
    # Documento
    numero_documento = db.Column(db.String(50), nullable=True)
    tipo_documento = db.Column(db.Enum('boleta', 'factura', 'recibo', 'otro',
                                      name='tipo_documento_enum'), 
                              default='boleta', nullable=False)
    
    # Archivo comprobante
    comprobante = db.Column(db.String(255), nullable=True)
    comprobante_original = db.Column(db.String(255), nullable=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, 
                                    onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    rendicion = db.relationship('Rendicion', back_populates='items')
    
    # Tipos de gasto predefinidos
    TIPOS_GASTO = [
        'Alimentación',
        'Transporte',
        'Alojamiento',
        'Combustible',
        'Peajes',
        'Estacionamiento',
        'Material de Oficina',
        'Servicios Profesionales',
        'Otros'
    ]
    
    def get_tipo_documento_display(self):
        """Obtiene el nombre legible del tipo de documento"""
        tipos = {
            'boleta': 'Boleta',
            'factura': 'Factura',
            'recibo': 'Recibo',
            'otro': 'Otro'
        }
        return tipos.get(self.tipo_documento, self.tipo_documento)
    
    def tiene_comprobante(self):
        """Verifica si el item tiene comprobante adjunto"""
        return bool(self.comprobante)
    
    def get_comprobante_url(self):
        """Obtiene la URL del comprobante"""
        if self.comprobante:
            return f'/uploads/comprobantes/{self.comprobante}'
        return None
    
    def __repr__(self):
        return f'<ItemRendicion {self.id} - {self.descripcion[:30]}>'
    
    def to_dict(self):
        """Convierte el item a diccionario"""
        return {
            'id': self.id,
            'rendicion_id': self.rendicion_id,
            'fecha_gasto': self.fecha_gasto.isoformat() if self.fecha_gasto else None,
            'tipo_gasto': self.tipo_gasto,
            'descripcion': self.descripcion,
            'proveedor': self.proveedor,
            'monto': float(self.monto) if self.monto else 0,
            'moneda': self.moneda,
            'numero_documento': self.numero_documento,
            'tipo_documento': self.tipo_documento,
            'tipo_documento_display': self.get_tipo_documento_display(),
            'tiene_comprobante': self.tiene_comprobante(),
            'comprobante_url': self.get_comprobante_url(),
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }