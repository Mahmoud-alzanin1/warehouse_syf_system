import os
import os.path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ================= SECURITY =================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ================= DATABASE =================
    # 🔥 أهم جزء (Render + Local + fallback آمن)
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # إصلاح Render القديم (postgres:// -> postgresql://)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

        # دعم psycopg2 بشكل صحيح
        if DATABASE_URL.startswith("postgresql://"):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local fallback (SQLite)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            basedir, "instance", "warehouse.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= ENGINE OPTIONS =================
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ================= PATHS =================
    PROJECT_ROOT = basedir
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

    UPLOAD_ROOT = os.path.join(INSTANCE_DIR, "uploads")
    WAYBILLS_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "waybills")
    BENEFICIARIES_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "beneficiaries")

    UPLOAD_FOLDER = UPLOAD_ROOT
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "jfif", "heic"}

    # ================= ADMIN ENV =================
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")