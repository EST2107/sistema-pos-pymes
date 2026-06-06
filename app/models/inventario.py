from app.extensions import db
from datetime import datetime
from app.utils.date_utils import nicaragua_now

class Inventario(db.Model):
    __tablename__ = 'inventario'

    id_inventario = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    id_sucursal = db.Column(db.Integer, nullable=True)
    stock_actual = db.Column(db.Numeric(12, 2), default=0.0)
    stock_minimo = db.Column(db.Numeric(12, 2), default=0.0)
    stock_maximo = db.Column(db.Numeric(12, 2), default=0.0)
    fecha_actualizacion = db.Column(db.DateTime, default=nicaragua_now, onupdate=nicaragua_now)

    producto = db.relationship('Producto', lazy=True)
