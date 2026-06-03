from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import require_roles
from app.models.auditoria import Auditoria
from app.extensions import db
from datetime import datetime

auditoria_bp = Blueprint("auditoria", __name__)

@auditoria_bp.route("/auditoria")
@login_required
@require_roles("Administrador")
def index():
    return render_template("auditoria/index.html")

@auditoria_bp.route("/api/auditoria")
@login_required
@require_roles("Administrador")
def api_auditoria():
    # Solo mostrar auditorías de la empresa actual
    query = Auditoria.query.filter_by(id_empresa=current_user.id_empresa)
    
    # Ordenar por fecha descendente
    query = query.order_by(Auditoria.fecha.desc())
    
    # Limitar a los últimos 500 registros para no sobrecargar
    auditorias = query.limit(500).all()
    
    return jsonify([a.to_dict() for a in auditorias])
