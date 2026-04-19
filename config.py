import os
import os.path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ================= SECURITY =================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ================= DATABASE =================
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

        if DATABASE_URL.startswith("postgresql://"):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            basedir, "instance", "warehouse.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= ENGINE =================
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ================= PATHS =================
    PROJECT_ROOT = basedir
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

    UPLOAD_ROOT = os.path.join(INSTANCE_DIR, "uploads")

    # 📦 تقسيم النظام (Inbound / Outbound / Data Entry)
    INBOUND_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "inbound")
    OUTBOUND_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "outbound")
    DATA_ENTRY_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "data_entry")

    WAYBILLS_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "waybills")
    BENEFICIARIES_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "beneficiaries")

    UPLOAD_FOLDER = UPLOAD_ROOT
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "jfif", "heic"}

    # ================= CLOUDINARY (🔥 مهم جداً) =================
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # ================= ADMIN =================
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")