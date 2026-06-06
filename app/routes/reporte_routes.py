from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from app.extensions import db
from datetime import datetime, timedelta

from app.utils.decorators import require_roles

reporte_bp = Blueprint("reporte", __name__, url_prefix="/reportes")

@reporte_bp.before_request
def check_roles():
    return require_roles('Administrador')


@reporte_bp.route("/")
@login_required
def index():
    return render_template("reportes/index.html")

@reporte_bp.route("/api/resumen_ventas", methods=["GET"])
@login_required
def api_resumen_ventas():
    try:
        hoy = datetime.now().date()
        start_date = hoy - timedelta(days=6)
        
        query = text("""
            SELECT DATE(fecha_venta) as fecha, SUM(total) as total_ventas
            FROM ventas
            WHERE id_empresa = :empresa AND estado = 'completada'
            AND DATE(fecha_venta) >= :start_date
            GROUP BY DATE(fecha_venta)
            ORDER BY fecha DESC
            LIMIT 7
        """)
        result = db.session.execute(query, {"empresa": current_user.id_empresa, "start_date": start_date}).fetchall()
        
        # Gastos
        query_gastos = text("""
            SELECT DATE(fecha_compra), SUM(total)
            FROM compras
            WHERE id_empresa = :empresa AND estado = 'completada'
            AND DATE(fecha_compra) >= :start_date
            GROUP BY DATE(fecha_compra)
        """)
        gastos_res = db.session.execute(query_gastos, {"empresa": current_user.id_empresa, "start_date": start_date}).fetchall()
        gastos_dict = {str(row[0]): float(row[1] or 0) for row in gastos_res}

        datos = []
        for row in result:
            fecha_str = str(row[0])
            total_ventas = float(row[1] or 0)
            gastos = gastos_dict.get(fecha_str, 0.0)
            datos.append({
                "fecha": fecha_str,
                "total": total_ventas,
                "ganancia": total_ventas - gastos,
                "gastos": gastos
            })
            
        return jsonify({"success": True, "data": datos[::-1]}) # Reverse to show chronologically
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@reporte_bp.route("/api/productos_top", methods=["GET"])
@login_required
def api_productos_top():
    try:
        # Consultar productos más vendidos de todos los tiempos o del mes (acá histórico)
        query = text("""
            SELECT p.nombre, SUM(dv.cantidad) as cantidad, SUM(dv.subtotal) as ingresos
            FROM detalle_ventas dv
            JOIN productos p ON dv.id_producto = p.id_producto
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE v.id_empresa = :empresa AND v.estado = 'completada'
            GROUP BY p.id_producto
            ORDER BY cantidad DESC
            LIMIT 5
        """)
        result = db.session.execute(query, {"empresa": current_user.id_empresa}).fetchall()
        
        datos = []
        for row in result:
            datos.append({
                "producto": row[0],
                "cantidad": float(row[1] or 0),
                "ingresos": float(row[2] or 0)
            })
            
        return jsonify({"success": True, "data": datos})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@reporte_bp.route("/api/stock_bajo", methods=["GET"])
@login_required
def api_stock_bajo():
    try:
        query = text("""
            SELECT p.nombre, i.stock_actual, i.stock_minimo
            FROM inventario i
            JOIN productos p ON i.id_producto = p.id_producto
            WHERE p.id_empresa = :empresa AND p.estado = 'activo'
            AND i.stock_actual <= i.stock_minimo
            ORDER BY i.stock_actual ASC
        """)
        result = db.session.execute(query, {"empresa": current_user.id_empresa}).fetchall()
        
        datos = []
        for row in result:
            datos.append({
                "producto": row[0],
                "stock_actual": float(row[1] or 0),
                "stock_minimo": float(row[2] or 0)
            })
            
        return jsonify({"success": True, "data": datos})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
