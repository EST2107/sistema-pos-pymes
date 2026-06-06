from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrar_db():
    app = create_app()
    with app.app_context():
        # Alterar tabla productos
        try:
            db.session.execute(text("ALTER TABLE productos ADD COLUMN imagen_datos LONGBLOB;"))
            print("Columna imagen_datos añadida a productos.")
        except Exception as e:
            print(f"Error o la columna ya existe en productos (imagen_datos): {e}")

        try:
            db.session.execute(text("ALTER TABLE productos ADD COLUMN imagen_mimetype VARCHAR(50);"))
            print("Columna imagen_mimetype añadida a productos.")
        except Exception as e:
            print(f"Error o la columna ya existe en productos (imagen_mimetype): {e}")

        # Alterar tabla usuarios
        try:
            db.session.execute(text("ALTER TABLE usuarios ADD COLUMN imagen_datos LONGBLOB;"))
            print("Columna imagen_datos añadida a usuarios.")
        except Exception as e:
            print(f"Error o la columna ya existe en usuarios (imagen_datos): {e}")

        try:
            db.session.execute(text("ALTER TABLE usuarios ADD COLUMN imagen_mimetype VARCHAR(50);"))
            print("Columna imagen_mimetype añadida a usuarios.")
        except Exception as e:
            print(f"Error o la columna ya existe en usuarios (imagen_mimetype): {e}")

        db.session.commit()
        print("Migración de imágenes completada.")

if __name__ == "__main__":
    migrar_db()
