from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.auditoria import Auditoria
import json

def registrar_auditoria(accion, modulo, detalles=None):
    """
    Registra una acción en el log de auditoría.
    """
    try:
        if not current_user.is_authenticated:
            return
            
        detalles_str = None
        if detalles:
            if isinstance(detalles, dict):
                detalles_str = json.dumps(detalles)
            else:
                detalles_str = str(detalles)
                
        ip = request.remote_addr if request else None
        
        auditoria = Auditoria(
            id_usuario=current_user.id_usuario,
            id_empresa=current_user.id_empresa,
            accion=accion,
            modulo=modulo,
            detalles=detalles_str,
            ip_address=ip
        )
        db.session.add(auditoria)
        db.session.commit()
    except Exception as e:
        print(f"Error registrando auditoría: {e}")
        db.session.rollback()
