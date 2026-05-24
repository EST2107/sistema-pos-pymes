from app.extensions import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'

    id_producto = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, nullable=True) # ForeignKey would go here if needed
    id_categoria = db.Column(db.Integer, nullable=True)
    id_marca = db.Column(db.Integer, nullable=True)
    id_unidad = db.Column(db.Integer, nullable=True)
    codigo = db.Column(db.String(80))
    codigo_barra = db.Column(db.String(100))
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio_compra = db.Column(db.Numeric(12, 2))
    precio_venta = db.Column(db.Numeric(12, 2), nullable=False)
    imagen_url = db.Column(db.String(255))
    aplica_impuesto = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Enum("activo", "inactivo"), default="activo")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships can be added later as needed
    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio_venta": float(self.precio_venta) if self.precio_venta else 0.0,
            "imagen_url": self.imagen_url
        }
