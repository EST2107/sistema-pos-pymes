from flask import Blueprint, render_template
from flask_login import login_required

venta_bp = Blueprint("venta", __name__, url_prefix="/ventas")

@venta_bp.route("/pos")
@login_required
def pos():
    return render_template("ventas/pos.html")
