from app import create_app
from app.extensions import db
from sqlalchemy import text
from app.models import Proveedor

app = create_app()

with app.app_context():
    prov = Proveedor.query.filter(Proveedor.nombre.ilike('%varios%')).first()
    if prov:
        print(f"FOUND PROVEEDOR VARIOS: ID={prov.id_proveedor}, Nombre='{prov.nombre}'")
        try:
            # Update any existing compras with null id_proveedor to this id
            db.session.execute(text(f"UPDATE compras SET id_proveedor = {prov.id_proveedor} WHERE id_proveedor IS NULL;"))
            # Revert the table definition to NOT NULL
            db.session.execute(text("ALTER TABLE compras MODIFY id_proveedor INT NOT NULL;"))
            db.session.commit()
            print("Successfully reverted id_proveedor to NOT NULL and updated existing records.")
        except Exception as e:
            print(f"Error altering table: {e}")
            db.session.rollback()
    else:
        print("COULD NOT FIND PROVEEDOR VARIOS!")
