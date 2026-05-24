from app import create_app
from app.extensions import db
from app.config.config import Config

app = create_app()
with app.app_context():
    db.create_all()
    db_type = Config.db_connection
    print(f"Database tables initialized successfully (using {db_type} connection).")

