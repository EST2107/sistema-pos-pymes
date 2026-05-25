from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from app.extensions import db

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
        # Consultar la vista de resumen de ventas de los últimos 7 días
        query = text("""
            SELECT fecha_venta, total_ventas, ganancia_estimada
            FROM vw_resumen_ventas_dia
            WHERE id_empresa = :empresa
            ORDER BY fecha_venta DESC
            LIMIT 7
        """)
        result = db.session.execute(query, {"empresa": current_user.id_empresa}).fetchall()
        
        # Gastos
        query_gastos = text("""
            SELECT DATE(fecha_compra), SUM(total)
            FROM compras
            WHERE id_empresa = :empresa AND estado = 'completada'
            GROUP BY DATE(fecha_compra)
        """)
        gastos_res = db.session.execute(query_gastos, {"empresa": current_user.id_empresa}).fetchall()
        gastos_dict = {str(row[0]): float(row[1] or 0) for row in gastos_res}

        datos = []
        for row in result:
            fecha_str = row[0].strftime("%Y-%m-%d")
            datos.append({
                "fecha": fecha_str,
                "total": float(row[1] or 0),
                "ganancia": float(row[2] or 0),
                "gastos": gastos_dict.get(fecha_str, 0.0)
            })
            
        return jsonify({"success": True, "data": datos[::-1]}) # Reverse to show chronologically
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@reporte_bp.route("/api/productos_top", methods=["GET"])
@login_required
def api_productos_top():
    try:
        # Consultar productos más vendidos
        query = text("""
            SELECT nombre_producto, cantidad_total_vendida, ingresos_generados
            FROM vw_productos_mas_vendidos
            WHERE id_empresa = :empresa
            ORDER BY cantidad_total_vendida DESC
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
