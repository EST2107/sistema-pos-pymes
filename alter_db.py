from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE compras ADD COLUMN tipo_compra VARCHAR(20) DEFAULT 'productos'"))
            print("Added tipo_compra")
        except Exception as e:
            print("Error adding tipo_compra:", e)
            
        try:
            conn.execute(text("ALTER TABLE compras ADD COLUMN descripcion_gasto VARCHAR(255)"))
            print("Added descripcion_gasto")
        except Exception as e:
            print("Error adding descripcion_gasto:", e)
            
        conn.commit()
        print("Database alterations completed.")
