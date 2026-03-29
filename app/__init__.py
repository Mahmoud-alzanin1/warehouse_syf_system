from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config
from app.core.database import db
from app.models.user import User

# Blueprints
from app.routes import main_bp
from app.auth.controller import auth_bp
from app.users.controller import users_bp
from app.data_entry.controller import data_entry_bp
from app.inbound.controller import inbound_bp
from app.distribution.controller import distribution_bp
from app.dashboard.controller import dashboard_bp
from app.admin.controller import admin_bp
from app.outbound.controller import outbound_bp

# ✅ Files blueprint (serving instance/uploads securely)
from app.files import files_bp


login_manager = LoginManager()
login_manager.login_view = "auth.login"

migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def _ensure_default_admin(app: Flask):
    """
    ✅ ينشئ أدمن افتراضي مرة واحدة فقط وبشكل آمن:
    - لا ينشئ أدمن إذا كانت البيانات غير موجودة بالـ ENV
    - لا يطبع كلمة المرور
    """
    username = app.config.get("DEFAULT_ADMIN_USERNAME")
    email = app.config.get("DEFAULT_ADMIN_EMAIL")
    password = app.config.get("DEFAULT_ADMIN_PASSWORD")

    # لو مش مزوّدين من ENV → ما نعملش أدمن
    if not (username and email and password):
        return

    # إذا فيه مستخدمين موجودين أصلًا → لا تعمل شيء
    if User.query.count() > 0:
        return

    admin = User(
        username=username.strip(),
        email=email.strip(),
        role="admin",
        is_admin=True,
        is_active_user=True,
        can_access_inbound=True,
        can_access_distribution=True,
        can_access_data_entry=True,
        can_access_dashboard=True,
        can_access_profile=True,
        can_access_outbound=True,
        can_access_admin_panel=True,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print("✅ Default admin created from ENV variables.")


def create_app(config_class: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # ✅ تحميل الموديلات + إنشاء أدمن اختياري
    with app.app_context():
        from app import models  # noqa: F401
        _ensure_default_admin(app)

    # ✅ تسجيل الـ Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")
    app.register_blueprint(inbound_bp, url_prefix="/inbound")
    app.register_blueprint(distribution_bp, url_prefix="/distribution")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(outbound_bp, url_prefix="/outbound")

    # ✅ Serve uploaded files (instance/uploads)
    app.register_blueprint(files_bp)

    # ✅ Inject warehouses — بدون كسر القوالب القديمة
    @app.context_processor
    def inject_warehouses():
        from app.models.warehouse import Warehouse

        try:
            warehouses = (
                Warehouse.query
                .filter_by(is_active=True)
                .order_by(Warehouse.name.asc())
                .all()
            )
        except Exception:
            warehouses = []

        return {
            "all_warehouses": warehouses,
            "warehouse_names": [w.name for w in warehouses],
        }

    return app
