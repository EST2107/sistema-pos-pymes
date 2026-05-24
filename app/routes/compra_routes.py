from flask import Blueprint, render_template
from flask_login import login_required

compra_bp = Blueprint("compra", __name__, url_prefix="/compras")

@compra_bp.route("/")
@login_required
def lista():
    return render_template("compras/lista.html")

@compra_bp.route("/detalle")
@login_required
def detalle():
    return render_template("compras/detalle.html")
