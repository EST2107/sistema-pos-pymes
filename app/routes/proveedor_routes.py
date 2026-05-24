from flask import Blueprint, render_template
from flask_login import login_required

proveedor_bp = Blueprint("proveedor", __name__, url_prefix="/proveedores")

@proveedor_bp.route("/")
@login_required
def lista():
    return render_template("proveedores/lista.html")
