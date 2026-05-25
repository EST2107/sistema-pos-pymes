from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Producto, Categoria, Inventario, Marca, UnidadMedida
from datetime import datetime

from app.utils.decorators import require_roles

producto_bp = Blueprint("producto", __name__, url_prefix="/productos")

@producto_bp.before_request
def check_roles():
    return require_roles('Administrador', 'Cajero', 'Inventario')


@producto_bp.route("/")
@login_required
def lista():
    return render_template("productos/lista.html")

@producto_bp.route("/api/list", methods=["GET"])
@login_required
def api_list():
    productos = Producto.query.filter_by(estado="activo").all()
    resultado = []
    for p in productos:
        cat = Categoria.query.get(p.id_categoria) if p.id_categoria else None
        inv = Inventario.query.filter_by(id_producto=p.id_producto).first()
        
        data = p.to_dict()
        data["categoria_nombre"] = cat.nombre if cat else "Sin Categoría"
        data["precio_compra"] = float(p.precio_compra) if p.precio_compra else 0.0
        data["stock"] = float(inv.stock_actual) if inv else 0.0
        data["estado"] = p.estado
        data["id_marca"] = p.id_marca
        data["id_unidad"] = p.id_unidad
        data["codigo_barra"] = p.codigo_barra
        data["descripcion"] = p.descripcion
        data["aplica_impuesto"] = p.aplica_impuesto
        resultado.append(data)
    return jsonify(resultado)

@producto_bp.route("/api/categorias", methods=["GET"])
@login_required
def api_categorias():
    categorias = Categoria.query.filter_by(estado="activo").all()
    return jsonify([c.to_dict() for c in categorias])

@producto_bp.route("/api/marcas", methods=["GET"])
@login_required
def api_marcas():
    marcas = Marca.query.filter_by(estado="activo").all()
    return jsonify([m.to_dict() for m in marcas])

@producto_bp.route("/api/marcas/crear", methods=["POST"])
@login_required
def api_marcas_crear():
    data = request.json
    try:
        nueva_marca = Marca(
            id_empresa=current_user.id_empresa,
            nombre=data.get("nombre", ""),
            estado="activo"
        )
        db.session.add(nueva_marca)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@producto_bp.route("/api/unidades", methods=["GET"])
@login_required
def api_unidades():
    unidades = UnidadMedida.query.filter_by(estado="activo").all()
    return jsonify([u.to_dict() for u in unidades])

@producto_bp.route("/api/crear", methods=["POST"])
@login_required
def api_crear():
    data = request.json
    try:
        nuevo_prod = Producto(
            id_empresa=current_user.id_empresa,
            id_categoria=data.get("id_categoria") or None,
            id_marca=data.get("id_marca") or None,
            id_unidad=data.get("id_unidad") or None,
            codigo=data.get("codigo", ""),
            codigo_barra=data.get("codigo_barra", ""),
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion", ""),
            precio_compra=float(data.get("precio_compra", 0.0)),
            precio_venta=float(data.get("precio_venta", 0.0)),
            aplica_impuesto=data.get("aplica_impuesto", False),
            estado="activo"
        )
        db.session.add(nuevo_prod)
        db.session.flush() # Get ID
        
        # Generar código automáticamente si no se proporcionó
        if not nuevo_prod.codigo or nuevo_prod.codigo.strip() == "":
            nuevo_prod.codigo = f"P{nuevo_prod.id_producto:03d}"
            
        # Crear inventario en 0
        nuevo_inv = Inventario(
            id_sucursal=current_user.id_sucursal,
            id_producto=nuevo_prod.id_producto,
            stock_actual=0.0,
            stock_minimo=0.0
        )
        db.session.add(nuevo_inv)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@producto_bp.route("/api/editar/<int:id>", methods=["PUT"])
@login_required
def api_editar(id):
    data = request.json
    try:
        prod = Producto.query.get_or_404(id)
        prod.codigo = data.get("codigo", prod.codigo)
        prod.codigo_barra = data.get("codigo_barra", prod.codigo_barra)
        prod.nombre = data.get("nombre", prod.nombre)
        prod.descripcion = data.get("descripcion", prod.descripcion)
        prod.id_categoria = data.get("id_categoria") or None
        prod.id_marca = data.get("id_marca") or None
        prod.id_unidad = data.get("id_unidad") or None
        prod.precio_compra = float(data.get("precio_compra", prod.precio_compra or 0.0))
        prod.precio_venta = float(data.get("precio_venta", prod.precio_venta))
        prod.aplica_impuesto = data.get("aplica_impuesto", prod.aplica_impuesto)
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@producto_bp.route("/api/eliminar/<int:id>", methods=["DELETE"])
@login_required
def api_eliminar(id):
    try:
        prod = Producto.query.get_or_404(id)
        prod.estado = "inactivo"
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@producto_bp.route("/api/entrada/<int:id>", methods=["POST"])
@login_required
def api_entrada(id):
    data = request.json
    cantidad = float(data.get("cantidad", 0.0))
    if cantidad <= 0:
        return jsonify({"success": False, "message": "Cantidad debe ser mayor a 0"}), 400
        
    try:
        inv = Inventario.query.filter_by(id_producto=id).first()
        if not inv:
            return jsonify({"success": False, "message": "Inventario no encontrado para este producto"}), 404
            
        inv.stock_actual = float(inv.stock_actual) + cantidad
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

