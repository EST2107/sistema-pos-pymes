from app.extensions import db
from datetime import datetime

class Compra(db.Model):
    __tablename__ = 'compras'

    id_compra = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, nullable=False)
    id_sucursal = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_proveedor = db.Column(db.Integer, nullable=True)
    numero_compra = db.Column(db.String(50), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), default=0.0)
    impuesto = db.Column(db.Numeric(10, 2), default=0.0)
    total = db.Column(db.Numeric(10, 2), default=0.0)
    estado = db.Column(db.Enum('completada', 'cancelada'), default='completada')
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_compra": self.id_compra,
            "numero_compra": self.numero_compra,
            "subtotal": float(self.subtotal),
            "total": float(self.total),
            "estado": self.estado,
            "fecha_compra": self.fecha_compra.strftime("%Y-%m-%d %H:%M:%S"),
            "id_proveedor": self.id_proveedor
        }
