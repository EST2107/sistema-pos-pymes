from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from app.models import Venta, Producto, DetalleVenta, Inventario
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Ventas del día
    ventas_hoy = float(db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha_venta) == today,
        Venta.estado == 'completada'
    ).scalar() or 0.0)

    # Ventas del mes
    ventas_mes = float(db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha_venta) >= first_day_of_month,
        Venta.estado == 'completada'
    ).scalar() or 0.0)

    # Total de productos activos
    total_productos = Producto.query.filter_by(estado='activo').count()
    
    # Productos con bajo stock (asumimos <= 5 para el demo si stock_minimo no se configuró)
    bajo_stock = db.session.query(Producto, Inventario).join(Inventario).filter(
        Inventario.stock_actual <= 5,
        Producto.estado == 'activo'
    ).limit(5).all()
    
    # Productos más vendidos (Top 4)
    mas_vendidos_query = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Producto.id_producto).order_by(db.desc('total_vendido')).limit(4).all()

    return render_template(
        "dashboard/dashboard.html",
        ventas_hoy=ventas_hoy,
        ventas_mes=ventas_mes,
        total_productos=total_productos,
        bajo_stock=bajo_stock,
        mas_vendidos=mas_vendidos_query
    )