from app.extensions import db
from datetime import datetime

class Auditoria(db.Model):
    __tablename__ = "auditorias"

    id_auditoria = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresas.id_empresa"), nullable=True)

    accion = db.Column(db.String(255), nullable=False)
    modulo = db.Column(db.String(100), nullable=False)
    detalles = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", lazy=True)

    def to_dict(self):
        return {
            "id_auditoria": self.id_auditoria,
            "id_usuario": self.id_usuario,
            "id_empresa": self.id_empresa,
            "accion": self.accion,
            "modulo": self.modulo,
            "detalles": self.detalles,
            "ip_address": self.ip_address,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S") if self.fecha else None,
            "nombre_usuario": self.usuario.usuario if self.usuario else "Sistema"
        }
