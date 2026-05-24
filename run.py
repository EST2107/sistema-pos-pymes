# run.py
from app import create_app

app = create_app()
print("DATABASE URI IN USE:", app.config.get("SQLALCHEMY_DATABASE_URI"))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)