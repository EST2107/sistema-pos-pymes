# config.py
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    db_connection = os.getenv("DB_CONNECTION", "mysql")
    
    if db_connection == "sqlite":
        SQLALCHEMY_DATABASE_URI = "sqlite:///pos_local.db"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:"
            f"{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False