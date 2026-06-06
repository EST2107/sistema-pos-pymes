from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from datetime import datetime, timedelta
import random
import string
import requests
import os
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
    
    # Determine phone number
    telefono = user.telefono
    if not telefono:
        return jsonify({"success": False, "message": "El usuario no tiene un número de teléfono registrado."})
        
    # Format phone number for Nicaragua
    telefono = telefono.strip()
    if not telefono.startswith('+'):
        # Clean non-digits just in case
        telefono = ''.join(filter(str.isdigit, telefono))
        telefono = f"+505{telefono}"
    
    # Send via Twilio WhatsApp
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    if twilio_sid and twilio_token and twilio_from:
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            payload = {
                "From": f"whatsapp:{twilio_from}",
                "To": f"whatsapp:{telefono}",
                "Body": f"🔒 POS Inventario\nHola {user.nombre_completo},\nTu código de acceso temporal es: *{codigo}*\n\nEste código expirará en 15 minutos."
            }
            auth = (twilio_sid, twilio_token)
            
            response = requests.post(url, data=payload, auth=auth)
            
            if response.status_code not in [200, 201]:
                print(f"Error Twilio: {response.text}")
                raise Exception("Twilio API Error")
                
        except Exception as e:
            print(f"Error al enviar WhatsApp: {e}")
            # Fallback a simulación
            print("=" * 50)
            print(f"📱 SIMULACIÓN DE WHATSAPP ENVIADO A: {telefono}")
            print(f"Tu código de acceso temporal es: {codigo}")
            print("=" * 50)
    else:
        # Simular envío
        print("=" * 50)
        print(f"📱 SIMULACIÓN DE WHATSAPP ENVIADO A: {telefono}")
        print(f"Hola {user.nombre_completo},")
        print(f"Tu código de acceso temporal es: {codigo}")
        print(f"Este código expirará en 15 minutos.")
        print("=" * 50)
    
    return jsonify({"success": True, "message": "Se ha enviado un código temporal por WhatsApp a tu número registrado."})

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
        
    if user.codigo_temporal and user.codigo_temporal == codigo:
        if user.expiracion_codigo and user.expiracion_codigo > datetime.now():
            # Code is valid, log user in
            user.codigo_temporal = None
            user.expiracion_codigo = None
            db.session.commit()
            
            login_user(user)
            registrar_auditoria("INICIO SESION", "Auth", f"Usuario logueado con código temporal")
            
            rol_nombre = user.rol.nombre if user.rol else ''
            if rol_nombre == 'Cajero':
                redirect_url = url_for("venta.historial")
            elif rol_nombre == 'Inventario':
                redirect_url = url_for("producto.lista")
            else:
                redirect_url = url_for("dashboard.dashboard")
                
            return jsonify({"success": True, "redirect_url": redirect_url})
        else:
            return jsonify({"success": False, "message": "El código temporal ha expirado."})
            
    return jsonify({"success": False, "message": "Código inválido."})