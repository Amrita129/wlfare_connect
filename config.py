import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "welfareconnect-production-secret-key-2026-secure")
    
    # Resolve SQLite database path deterministically inside instance/ directory
    default_sqlite_path = os.path.join(basedir, "instance", "welfare.db")
    raw_db_url = os.getenv("DATABASE_URL")
    
    if not raw_db_url:
        DATABASE_URL = f"sqlite:///{default_sqlite_path}"
    elif raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = raw_db_url

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
