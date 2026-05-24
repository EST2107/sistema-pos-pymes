from flask import Blueprint, render_template
from flask_login import login_required

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuarios")

@usuario_bp.route("/")
@login_required
def lista():
    return render_template("usuarios/lista.html")
