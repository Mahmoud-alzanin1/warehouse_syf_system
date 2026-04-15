import os
import os.path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ---------------- Security ----------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ---------------- Database ----------------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "instance", "warehouse.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # إصلاح Render PostgreSQL (مهم جدًا)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    # ---------------- SQL Engine Options ----------------
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ---------------- Paths ----------------
    PROJECT_ROOT = basedir
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

    UPLOAD_ROOT = os.path.join(INSTANCE_DIR, "uploads")
    WAYBILLS_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "waybills")
    BENEFICIARIES_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "beneficiaries")

    UPLOAD_FOLDER = UPLOAD_ROOT

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "jfif", "heic"}

    # ---------------- Admin ENV ----------------
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")