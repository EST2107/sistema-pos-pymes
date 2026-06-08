from flask import abort, redirect, url_for, flash, request, jsonify
from flask_login import current_user

def require_roles(*roles):
    if not current_user.is_authenticated:
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "No autenticado"}), 401
        flash("Debes iniciar sesión para acceder.", "warning")
        return redirect(url_for('auth.login'))
        
    if not current_user.rol or current_user.rol.nombre not in roles:
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Acceso denegado"}), 403
        flash("No tienes permisos para acceder a esta página.", "danger")
        return redirect(url_for('dashboard.dashboard'))
