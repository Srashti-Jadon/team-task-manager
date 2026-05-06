import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    DATABASE_URL = os.environ.get('DATABASE_URL')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False