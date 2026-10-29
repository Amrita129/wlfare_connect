import os
import secrets
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def get_secret_key():
    """
    Retrieve SECRET_KEY securely:
    - In production: enforce that a strong, non-placeholder SECRET_KEY is set via environment.
    - In development: load or generate a persistent local secret key stored in instance/.secret_key (ignored by Git).
    """
    key = os.getenv("SECRET_KEY")
    env = (os.getenv("FLASK_ENV") or os.getenv("ENV") or "").lower()

    insecure_placeholders = {
        "change-this-in-production",
        "welfareconnect-production-secret-key-2026-secure",
        "secret",
        "secret-key",
        "default",
        "password",
    }

    if env == "production":
        if not key or key.strip() in insecure_placeholders:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: A valid, non-placeholder SECRET_KEY "
                "environment variable must be provided when running in production."
            )
        return key.strip()

    if key and key.strip() not in insecure_placeholders:
        return key.strip()

    # For local development: read or create persistent local secret key outside Git
    instance_dir = os.path.join(basedir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    key_file = os.path.join(instance_dir, ".secret_key")

    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved:
                    return saved
        except Exception:
            pass

    generated = secrets.token_hex(32)
    try:
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(generated)
    except Exception:
        pass
    return generated


def get_database_url():
    """
    Resolve DATABASE_URL deterministically:
    - Normalizes postgres:// to postgresql:// for SQLAlchemy/psycopg2.
    - Resolves relative SQLite URIs into absolute paths inside instance/ so worker/script CWD changes do not cause database divergence.
    - Defaults to instance/welfare.db if unset.
    """
    raw_db_url = os.getenv("DATABASE_URL")
    default_sqlite_path = os.path.join(basedir, "instance", "welfare.db")

    if not raw_db_url:
        return f"sqlite:///{default_sqlite_path}"

    if raw_db_url.startswith("postgres://"):
        return raw_db_url.replace("postgres://", "postgresql://", 1)

    # Normalize relative SQLite paths (e.g. sqlite:///welfare.db) to deterministic location inside instance/
    if raw_db_url.startswith("sqlite:///") and not raw_db_url.startswith("sqlite:////"):
        path_part = raw_db_url[len("sqlite:///"):]
        if not os.path.isabs(path_part):
            abs_path = os.path.abspath(os.path.join(basedir, "instance", path_part))
            return f"sqlite:///{abs_path}"

    return raw_db_url


class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

