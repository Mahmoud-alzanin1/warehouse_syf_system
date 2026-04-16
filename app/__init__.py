import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config
from app.core.database import db
from app.models.user import User
from app.models.warehouse import Warehouse

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


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import models  # noqa

   

        # ================= ADMIN =================
        username = app.config.get("DEFAULT_ADMIN_USERNAME")
        email = app.config.get("DEFAULT_ADMIN_EMAIL")
        password = app.config.get("DEFAULT_ADMIN_PASSWORD")

        if username and email and password:
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
            print("✅ Default admin created")

        # ================= WAREHOUSES =================
        warehouses_list = [
            "SYF-Abu Rashid",
            "FPDSYFS17",
            "AL-Migdad",
            "Abu Zayed Store",
            "Al-Zawaida Club SYFS",
        ]

        for name in warehouses_list:
            db.session.add(Warehouse(name=name, is_active=True))

        db.session.commit()
        print("✅ Warehouses added")

        # ================= FOLDERS =================
        os.makedirs(app.config["WAYBILLS_UPLOAD_DIR"], exist_ok=True)
        os.makedirs(app.config["BENEFICIARIES_UPLOAD_DIR"], exist_ok=True)

    # ================= BLUEPRINTS =================
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")
    app.register_blueprint(inbound_bp, url_prefix="/inbound")
    app.register_blueprint(distribution_bp, url_prefix="/distribution")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(outbound_bp, url_prefix="/outbound")
    app.register_blueprint(files_bp)

    @app.context_processor
    def inject_warehouses():
        try:
            warehouses = Warehouse.query.filter_by(is_active=True).all()
        except Exception:
            warehouses = []

        return {
            "all_warehouses": warehouses,
            "warehouse_names": [w.name for w in warehouses],
        }

    return app