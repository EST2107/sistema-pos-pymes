from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from app.models import Venta, Producto, DetalleVenta, Inventario, Compra
from datetime import datetime, timedelta
from sqlalchemy import func, text

from app.utils.decorators import require_roles

dashboard_bp = Blueprint("dashboard", __name__)

from flask import redirect, url_for
from flask_login import current_user

@dashboard_bp.before_request
def check_roles():
    if current_user.is_authenticated and current_user.rol:
        if current_user.rol.nombre == 'Cajero':
            return redirect(url_for('venta.historial'))
        elif current_user.rol.nombre == 'Inventario':
            return redirect(url_for('producto.lista'))
            
    return require_roles('Administrador')



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

    # Gastos del mes (compras)
    gastos_mes = float(db.session.query(func.sum(Compra.total)).filter(
        func.date(Compra.fecha_compra) >= first_day_of_month,
        Compra.estado == 'completada'
    ).scalar() or 0.0)

    # Total de productos activos
    total_productos = Producto.query.filter_by(estado='activo').count()
    
    # Productos con bajo stock
    bajo_stock = db.session.query(Producto, Inventario).join(Inventario).filter(
        Inventario.stock_actual <= Inventario.stock_minimo,
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
        gastos_mes=gastos_mes,
        total_productos=total_productos,
        bajo_stock=bajo_stock,
        mas_vendidos=mas_vendidos_query
    )

@dashboard_bp.route("/api/dashboard_charts")
@login_required
def api_dashboard_charts():
    # 1. Ventas ultimos 7 dias (Rellenar días vacíos)
    hoy = datetime.now().date()
    ultimos_7_dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
    
    start_date = hoy - timedelta(days=6)
    
    query_7d = text("""
        SELECT DATE(fecha_venta) as fecha, SUM(total) as total_ventas 
        FROM ventas 
        WHERE id_empresa = :empresa AND estado = 'completada' 
        AND DATE(fecha_venta) >= :start_date
        GROUP BY DATE(fecha_venta)
        ORDER BY fecha DESC
    """)
    res_7d = db.session.execute(query_7d, {"empresa": current_user.id_empresa, "start_date": start_date}).fetchall()
    
    # Mapear ventas reales por fecha
    # Dependiendo del conector, row[0] puede ser string o date. Nos aseguramos de compararlo como string.
    ventas_dict = {str(row[0]): float(row[1] or 0) for row in res_7d}
    
    ventas_7d = []
    for dia in ultimos_7_dias:
        str_dia = str(dia)
        ventas_7d.append({
            "fecha": dia.strftime("%d/%m"),
            "total": ventas_dict.get(str_dia, 0.0)
        })
    
    # 2. Ventas por categoría
    query_cat = text("""
        SELECT c.nombre, sum(dv.subtotal) as total
        FROM detalle_ventas dv
        JOIN productos p ON dv.id_producto = p.id_producto
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN ventas v ON dv.id_venta = v.id_venta
        WHERE v.id_empresa = :empresa AND v.estado = 'completada'
        GROUP BY c.nombre
    """)
    res_cat = db.session.execute(query_cat, {"empresa": current_user.id_empresa}).fetchall()
    
    ventas_cat = []
    for row in res_cat:
        ventas_cat.append({
            "categoria": row[0],
            "total": float(row[1] or 0)
        })
        
    # Si no hay ventas, mostramos un 'Sin ventas'
    if not ventas_cat:
        ventas_cat.append({"categoria": "Sin ventas", "total": 0})
        
    return {"ventas_7d": ventas_7d, "ventas_cat": ventas_cat}