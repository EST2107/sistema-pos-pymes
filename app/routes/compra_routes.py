from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Compra, DetalleCompra, Producto, Proveedor, Inventario
from datetime import datetime

compra_bp = Blueprint("compra", __name__, url_prefix="/compras")

@compra_bp.route("/")
@login_required
def lista():
    return render_template("compras/lista.html")

@compra_bp.route("/api/list", methods=["GET"])
@login_required
def api_list():
    compras = Compra.query.filter_by(id_empresa=current_user.id_empresa).order_by(Compra.fecha_compra.desc()).all()
    res = []
    for c in compras:
        prov = Proveedor.query.get(c.id_proveedor) if c.id_proveedor else None
        d = c.to_dict()
        d["proveedor_nombre"] = prov.nombre if prov else "Desconocido"
        res.append(d)
    return jsonify(res)

@compra_bp.route("/api/crear", methods=["POST"])
@login_required
def api_crear():
    data = request.json
    id_proveedor = data.get("id_proveedor")
    items = data.get("items", [])
    
    if not items:
        return jsonify({"success": False, "message": "No hay productos en la compra"}), 400
        
    try:
        subtotal_compra = 0.0
        num_compra = f"C-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        nueva_compra = Compra(
            id_empresa=current_user.id_empresa,
            id_sucursal=current_user.id_sucursal,
            id_usuario=current_user.id_usuario,
            id_proveedor=id_proveedor,
            numero_compra=num_compra,
            subtotal=0.0,
            impuesto=0.0,
            total=0.0,
            estado="completada"
        )
        db.session.add(nueva_compra)
        db.session.flush()
        
        for item in items:
            producto_id = item.get("id_producto")
            cantidad = float(item.get("cantidad", 0))
            costo_unitario = float(item.get("costo_unitario", 0))
            subtotal_item = cantidad * costo_unitario
            subtotal_compra += subtotal_item
            
            detalle = DetalleCompra(
                id_compra=nueva_compra.id_compra,
                id_producto=producto_id,
                cantidad=cantidad,
                precio_unitario=costo_unitario,
                subtotal=subtotal_item
            )
            db.session.add(detalle)
            
            # Sumar al inventario
            inv = Inventario.query.filter_by(id_producto=producto_id).first()
            if inv:
                inv.stock_actual = float(inv.stock_actual) + cantidad
            else:
                inv = Inventario(
                    id_sucursal=current_user.id_sucursal,
                    id_producto=producto_id,
                    stock_actual=cantidad,
                    stock_minimo=0
                )
                db.session.add(inv)
                
        nueva_compra.subtotal = subtotal_compra
        nueva_compra.total = subtotal_compra # Asumimos 0 impuesto por ahora
        
        db.session.commit()
        return jsonify({"success": True, "message": "Compra registrada exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@compra_bp.route("/api/detalle/<int:id>", methods=["GET"])
@login_required
def api_detalle(id):
    try:
        compra = Compra.query.get_or_404(id)
        if compra.id_empresa != current_user.id_empresa:
            return jsonify({"success": False, "message": "Acceso denegado"}), 403
            
        detalles = DetalleCompra.query.filter_by(id_compra=id).all()
        res_detalles = []
        for d in detalles:
            prod = Producto.query.get(d.id_producto)
            dt = d.to_dict()
            dt["producto_nombre"] = prod.nombre if prod else "Desconocido"
            res_detalles.append(dt)
            
        return jsonify({"success": True, "detalles": res_detalles})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
