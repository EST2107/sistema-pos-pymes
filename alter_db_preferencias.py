import os
from sqlalchemy import text
from app import create_app
from app.extensions import db

app = create_app()

def run_migration():
    with app.app_context():
        try:
            # Check if columns exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            
            with db.engine.connect() as connection:
                if 'tema_preferido' not in columns:
                    print("Agregando columna 'tema_preferido'...")
                    connection.execute(text("ALTER TABLE usuarios ADD COLUMN tema_preferido VARCHAR(20) DEFAULT 'light';"))
                
                if 'color_primario' not in columns:
                    print("Agregando columna 'color_primario'...")
                    connection.execute(text("ALTER TABLE usuarios ADD COLUMN color_primario VARCHAR(20) DEFAULT '#0b5cff';"))
                
                connection.commit()
            print("Migración completada exitosamente.")
        except Exception as e:
            print(f"Error en la migración: {e}")

if __name__ == "__main__":
    run_migration()
