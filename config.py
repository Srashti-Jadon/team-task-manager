import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    DB_URL = os.environ.get('DATABASE_URL')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    if DB_URL and DB_URL.strip() != "":
        SQLALCHEMY_DATABASE_URI = DB_URL.replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False