from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE compras MODIFY id_proveedor INT NULL;"))
        db.session.commit()
        print("Successfully modified id_proveedor to allow NULL values.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
