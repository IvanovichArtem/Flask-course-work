import os

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", "postgresql://admin:root@db:5432/flask_museum"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "SECRET_KEY very long"
SESSION_TYPE = "filesystem"
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 30
UPLOAD_FOLDER = "app/media"
