from flask_login import UserMixin
from app.extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)

    id_empresa = db.Column(db.Integer, db.ForeignKey("empresas.id_empresa"), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursales.id_sucursal"))
    id_rol = db.Column(db.Integer, db.ForeignKey("roles.id_rol"), nullable=False)

    usuario = db.Column(db.String(80), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    imagen_url = db.Column(db.String(255))
    estado = db.Column(db.Enum("activo", "inactivo", "bloqueado"), default="activo")
    ultimo_acceso = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime)

    codigo_temporal = db.Column(db.String(10), nullable=True)
    expiracion_codigo = db.Column(db.DateTime, nullable=True)

    empresa = db.relationship("Empresa", lazy=True)
    sucursal = db.relationship("Sucursal", lazy=True)
    rol = db.relationship("Rol", lazy=True)

    def get_id(self):
        return str(self.id_usuario)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "id_rol": self.id_rol,
            "usuario": self.usuario,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "telefono": self.telefono,
            "imagen_url": self.imagen_url,
            "estado": self.estado
        }