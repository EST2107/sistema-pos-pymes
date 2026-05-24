from flask import Blueprint, render_template
from flask_login import login_required

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")

@inventario_bp.route("/")
@login_required
def lista():
    return render_template("inventario/lista.html")
