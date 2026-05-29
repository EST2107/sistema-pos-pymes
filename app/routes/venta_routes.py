from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Producto, Cliente, Venta, DetalleVenta, Inventario
from datetime import datetime

from app.utils.decorators import require_roles

venta_bp = Blueprint("venta", __name__, url_prefix="/ventas")

@venta_bp.before_request
def check_roles():
    return require_roles('Administrador', 'Cajero')


@venta_bp.route("/pos")
@login_required
def pos():
    return render_template("ventas/pos.html")

@venta_bp.route("/historial")
@login_required
def historial():
    return render_template("ventas/historial.html")

@venta_bp.route("/api/historial", methods=["GET"])
@login_required
def api_historial():
    ventas = Venta.query.filter_by(id_empresa=current_user.id_empresa).order_by(Venta.fecha_venta.desc()).all()
    res = []
    for v in ventas:
        cliente = Cliente.query.get(v.id_cliente) if v.id_cliente else None
        d = v.to_dict()
        d["cliente"] = cliente.nombre if cliente else "Público General"
        res.append(d)
    return jsonify(res)

@venta_bp.route("/api/productos", methods=["GET"])
@login_required
def api_productos():
    # Obtener productos activos
    productos = Producto.query.filter_by(estado="activo").all()
    resultado = []
    for p in productos:
        # Obtener inventario para este producto (asumimos que hay un registro o sumamos si hay por sucursal)
        inv = Inventario.query.filter_by(id_producto=p.id_producto).first()
        stock = float(inv.stock_actual) if inv else 0.0
        
        # Opcional: Solo retornar productos con stock > 0 si así se desea
        # if stock <= 0: continue
        
        data = p.to_dict()
        data["stock"] = stock
        resultado.append(data)
        
    return jsonify(resultado)

@venta_bp.route("/api/clientes", methods=["GET"])
@login_required
def api_clientes():
    clientes = Cliente.query.filter_by(estado="activo").all()
    return jsonify([c.to_dict() for c in clientes])

@venta_bp.route("/api/cobrar", methods=["POST"])
@login_required
def api_cobrar():
    data = request.json
    cart = data.get("cart", [])
    descuento = float(data.get("descuento", 0.0))
    propina = float(data.get("propina", 0.0))
    metodo_pago = data.get("metodo_pago", "Efectivo")
    id_cliente = data.get("id_cliente") # Puede ser None (Público General)
    
    if not cart:
        return jsonify({"success": False, "message": "El carrito está vacío"}), 400
        
    try:
        subtotal_venta = 0.0
        
        # Crear objeto Venta primero para calcular el total
        # Generar número de venta (simple timestamp o uuid, aquí usamos un prefijo simple)
        num_venta = f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        nueva_venta = Venta(
            id_empresa=current_user.id_empresa,
            id_sucursal=current_user.id_sucursal,
            id_usuario=current_user.id_usuario,
            id_cliente=id_cliente if id_cliente else None,
            numero_venta=num_venta,
            descuento=descuento,
            impuesto=0.0,  # IVA por producto se implementará después
            propina=propina,
            metodo_pago=metodo_pago,
            estado="completada",
            total=0.0,
            subtotal=0.0
        )
        db.session.add(nueva_venta)
        db.session.flush() # Para obtener el id_venta
        
        for item in cart:
            producto_id = item.get("id_producto")
            cantidad = float(item.get("cantidad"))
            precio = float(item.get("precio"))
            subtotal_item = cantidad * precio
            subtotal_venta += subtotal_item
            
            detalle = DetalleVenta(
                id_venta=nueva_venta.id_venta,
                id_producto=producto_id,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=0.0,
                subtotal=subtotal_item
            )
            db.session.add(detalle)
            
            # Descontar inventario
            inv = Inventario.query.filter_by(id_producto=producto_id).first()
            if inv:
                if float(inv.stock_actual) < cantidad:
                    raise Exception(f"Stock insuficiente para el producto ID {producto_id}")
                inv.stock_actual = float(inv.stock_actual) - cantidad
            else:
                raise Exception(f"No hay registro de inventario para el producto ID {producto_id}")
                
        # Actualizar totales
        nueva_venta.subtotal = subtotal_venta
        nueva_venta.total = subtotal_venta - descuento + propina
        
        db.session.commit()
        return jsonify({"success": True, "message": "Venta procesada exitosamente", "venta_id": nueva_venta.id_venta})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@venta_bp.route("/factura/<int:id_venta>", methods=["GET"])
@login_required
def ver_factura(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    # Get details with products
    detalles = DetalleVenta.query.filter_by(id_venta=id_venta).all()
    
    return render_template("ventas/factura.html", venta=venta, detalles=detalles)
