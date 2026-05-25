from flask import abort
from flask_login import current_user

def require_roles(*roles):
    if not current_user.is_authenticated:
        return abort(401)
    if not current_user.rol or current_user.rol.nombre not in roles:
        return abort(403)
