from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from datetime import datetime, timedelta
import random
import string
from app.extensions import db

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
        
        # Check normal password OR check active temporary code
        is_valid_password = False
        if user and user.estado == "activo":
            if verificar_password(user.password_hash, password):
                is_valid_password = True
            elif user.codigo_temporal and user.codigo_temporal == password:
                # Validate expiration
                if user.expiracion_codigo and user.expiracion_codigo > datetime.now():
                    is_valid_password = True
                    # Invalidate code after use
                    user.codigo_temporal = None
                    user.expiracion_codigo = None
                    db.session.commit()
                else:
                    flash("El código temporal ha expirado.", "danger")

        if is_valid_password:
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

@auth_bp.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    correo = data.get("correo")
    
    if not correo:
        return jsonify({"success": False, "message": "Correo es requerido."})
        
    user = Usuario.query.filter_by(correo=correo).first()
    if not user:
        # Prevent user enumeration, just say it was sent if email not found
        return jsonify({"success": True, "message": "Si el correo existe, se ha enviado un código temporal."})
        
    # Generate 6 digit code
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_temporal = codigo
    user.expiracion_codigo = datetime.now() + timedelta(minutes=15)
    db.session.commit()
    
    # Simular envío de correo en la terminal
    print("=" * 50)
    print(f"📧 SIMULACIÓN DE CORREO ENVIADO A: {correo}")
    print(f"Estimado/a {user.nombre_completo},")
    print(f"Tu código de acceso temporal es: {codigo}")
    print(f"Este código expirará en 15 minutos.")
    print("=" * 50)
    
    return jsonify({"success": True, "message": "Si el correo existe, se ha enviado un código temporal."})