from flask import Blueprint, render_template
from flask_login import login_required

producto_bp = Blueprint("producto", __name__, url_prefix="/productos")

@producto_bp.route("/")
@login_required
def lista():
    return render_template("productos/lista.html")
