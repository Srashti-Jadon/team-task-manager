import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # FIX for SQLAlchemy 2.x compatibility
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(BASE_DIR / "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False