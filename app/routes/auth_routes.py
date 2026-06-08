from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from datetime import datetime, timedelta
import random
import string
import requests
import os
from app.extensions import db

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models.usuario import Usuario, RecuperacionPassword
from app.services.auth_service import verificar_password, generar_password
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
        return jsonify({"success": False, "message": "Este correo electrónico no está registrado en el sistema."})
        
    # Generate 6 digit code
    codigo = ''.join(random.choices(string.digits, k=6))
    
    # Invalidate previous codes
    RecuperacionPassword.query.filter_by(usuario_id=user.id_usuario, usado=False).update({"usado": True})
    
    # Save new code
    nueva_recuperacion = RecuperacionPassword(
        usuario_id=user.id_usuario,
        codigo=codigo,
        fecha_expiracion=datetime.now() + timedelta(minutes=15)
    )
    db.session.add(nueva_recuperacion)
    db.session.commit()
    
    # Enviar por Email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = correo
            msg['Subject'] = "Recuperación de Contraseña - POS Inventario"
            
            body = f"Hola {user.nombre_completo},\n\nHas solicitado recuperar tu contraseña.\nTu código de verificación es: {codigo}\n\nEste código expira en 15 minutos."
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text_str = msg.as_string()
            server.sendmail(smtp_user, correo, text_str)
            server.quit()
            return jsonify({"success": True, "message": "Se ha enviado un código de recuperación a tu correo electrónico."})
        except Exception as e:
            print(f"Error enviando correo: {e}")
            print(f"SIMULACIÓN EMAIL -> {correo} | Código: {codigo}")
            return jsonify({"success": True, "message": f"(Modo Prueba) Error enviando correo. El código es: {codigo}"})
    else:
        # Simular envío si no hay configuración
        print("=" * 50)
        print(f"SIMULACION DE EMAIL ENVIADO A: {correo}")
        print(f"Tu codigo de recuperacion es: {codigo}")
        print("=" * 50)
        return jsonify({"success": True, "message": f"(Modo Prueba - Sin SMTP) Tu código de recuperación es: {codigo}"})

@auth_bp.route("/api/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    correo = data.get("correo")
    codigo = data.get("codigo")
    
    if not correo or not codigo:
        return jsonify({"success": False, "message": "Correo y código son requeridos."})
        
    user = Usuario.query.filter_by(correo=correo).first()
    if not user or user.estado != "activo":
        return jsonify({"success": False, "message": "Código inválido o expirado."})
        
    recuperacion = RecuperacionPassword.query.filter_by(
        usuario_id=user.id_usuario,
        codigo=codigo,
        usado=False
    ).first()
    
    if recuperacion and recuperacion.fecha_expiracion > datetime.now():
        return jsonify({"success": True, "message": "Código verificado."})
        
    return jsonify({"success": False, "message": "El código es inválido o ha expirado."})

@auth_bp.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    correo = data.get("correo")
    codigo = data.get("codigo")
    nueva_password = data.get("nueva_password")
    
    if not correo or not codigo or not nueva_password:
        return jsonify({"success": False, "message": "Faltan datos requeridos."})
        
    user = Usuario.query.filter_by(correo=correo).first()
    if not user:
        return jsonify({"success": False, "message": "Usuario no encontrado."})
        
    recuperacion = RecuperacionPassword.query.filter_by(
        usuario_id=user.id_usuario,
        codigo=codigo,
        usado=False
    ).first()
    
    if recuperacion and recuperacion.fecha_expiracion > datetime.now():
        # Actualizar contraseña
        user.password_hash = generar_password(nueva_password)
        recuperacion.usado = True
        db.session.commit()
        
        registrar_auditoria("ACTUALIZAR CONTRASENA", "Auth", f"Usuario {user.usuario} restableció su contraseña.")
        return jsonify({"success": True, "message": "Contraseña actualizada correctamente."})
        
    return jsonify({"success": False, "message": "No se pudo restablecer la contraseña. El código es inválido o ha expirado."})