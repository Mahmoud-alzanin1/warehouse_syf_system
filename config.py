import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 🔐 المفتاح السري للجلسات (غيّره في البيئة في الإنتاج)
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-me"

    # ---------------- Database ----------------
    # على السيرفر: استخدم DATABASE_URL مثل:
    # postgresql://user:pass@host:5432/dbname
    DB_URL_ENV = os.environ.get("DATABASE_URL")
    if DB_URL_ENV:
        SQLALCHEMY_DATABASE_URI = DB_URL_ENV
    else:
        # محليًا: خليها داخل instance (أفضل من app.db داخل الجذر)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "warehouse.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔹 خيارات إضافية للمحرك (تفيد أكثر مع PostgreSQL/MySQL)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # ---------------- Uploads (Production Safe) ----------------
    PROJECT_ROOT = basedir
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

    # Root uploads folder inside instance (NOT public)
    UPLOAD_ROOT = os.path.join(INSTANCE_DIR, "uploads")
    WAYBILLS_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "waybills")
    BENEFICIARIES_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "beneficiaries")

    # استخدم هذا كـ fallback عام لو في أماكن بالكود بتقرأ UPLOAD_FOLDER
    UPLOAD_FOLDER = UPLOAD_ROOT

    # Limits & types
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "jfif", "heic"}


    # Ensure folders exist
    os.makedirs(WAYBILLS_UPLOAD_DIR, exist_ok=True)
    os.makedirs(BENEFICIARIES_UPLOAD_DIR, exist_ok=True)

    # ✅ (تحضير) CSRF لاحقًا
    WTF_CSRF_ENABLED = True

    # ✅ (آمن) بيانات الأدمن الافتراضي من ENV فقط
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")
