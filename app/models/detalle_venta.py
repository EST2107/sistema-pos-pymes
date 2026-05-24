from app.extensions import db

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'

    id_detalle_venta = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Numeric(12, 2), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    descuento = db.Column(db.Numeric(12, 2), default=0.0)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    producto = db.relationship('Producto', lazy=True)
