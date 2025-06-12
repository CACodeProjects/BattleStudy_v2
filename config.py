import os

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///default.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
