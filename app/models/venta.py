from app.extensions import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'

    id_venta = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, nullable=True)
    id_sucursal = db.Column(db.Integer, nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=True)
    numero_venta = db.Column(db.String(50), nullable=True)
    subtotal = db.Column(db.Numeric(12, 2), default=0.0)
    descuento = db.Column(db.Numeric(12, 2), default=0.0)
    impuesto = db.Column(db.Numeric(12, 2), default=0.0)
    propina = db.Column(db.Numeric(12, 2), default=0.0)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    monto_recibido = db.Column(db.Numeric(12, 2), default=0.0)
    cambio = db.Column(db.Numeric(12, 2), default=0.0)
    estado = db.Column(db.Enum("completada", "anulada", "pendiente"), default="completada")
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade="all, delete-orphan")
    usuario = db.relationship('Usuario', lazy=True)
    cliente = db.relationship('Cliente', lazy=True)

    def to_dict(self):
        return {
            "id_venta": self.id_venta,
            "numero_venta": self.numero_venta,
            "subtotal": float(self.subtotal) if self.subtotal else 0.0,
            "descuento": float(self.descuento) if self.descuento else 0.0,
            "impuesto": float(self.impuesto) if self.impuesto else 0.0,
            "total": float(self.total) if self.total else 0.0,
            "estado": self.estado,
            "fecha_venta": self.fecha_venta.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_venta else ""
        }
