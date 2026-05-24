from flask import Blueprint, render_template
from flask_login import login_required

reporte_bp = Blueprint("reporte", __name__, url_prefix="/reportes")

@reporte_bp.route("/")
@login_required
def lista():
    return render_template("reportes/lista.html")
