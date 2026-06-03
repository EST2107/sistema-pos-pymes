from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.models.usuario import Usuario
from app.services.auth_service import verificar_password
from app.services.auditoria_service import registrar_auditoria

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        user = Usuario.query.filter_by(usuario=usuario).first()

        if user and user.estado == "activo" and verificar_password(user.password_hash, password):
            login_user(user)
            registrar_auditoria("INICIO SESION", "Auth", f"Usuario logueado exitosamente")
            
            rol_nombre = user.rol.nombre if user.rol else ''
            if rol_nombre == 'Cajero':
                return redirect(url_for("venta.historial"))
            elif rol_nombre == 'Inventario':
                return redirect(url_for("producto.lista"))
                
            return redirect(url_for("dashboard.dashboard"))

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    registrar_auditoria("CIERRE SESION", "Auth", "Usuario cerró sesión")
    logout_user()
    return redirect(url_for("auth.login"))