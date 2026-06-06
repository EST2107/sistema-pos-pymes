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
    imagen_datos = db.Column(db.LargeBinary)
    imagen_mimetype = db.Column(db.String(50))
    aplica_impuesto = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Enum("activo", "inactivo"), default="activo")
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    # Relationships can be added later as needed
    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "id_categoria": self.id_categoria,
            "id_marca": self.id_marca,
            "id_unidad": self.id_unidad,
            "codigo": self.codigo,
            "codigo_barra": self.codigo_barra,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio_compra": float(self.precio_compra) if self.precio_compra else 0.0,
            "precio_venta": float(self.precio_venta) if self.precio_venta else 0.0,
            "aplica_impuesto": self.aplica_impuesto,
            "imagen_url": self.imagen_url or None
        }
