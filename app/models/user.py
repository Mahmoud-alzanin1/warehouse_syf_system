from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.core.database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(32), default="viewer", nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    is_active_user = db.Column(db.Boolean, default=True)

    # ✅ صلاحيات الوصول
    can_access_inbound = db.Column(db.Boolean, default=False)
    can_access_distribution = db.Column(db.Boolean, default=False)
    can_access_data_entry = db.Column(db.Boolean, default=False)
    can_access_dashboard = db.Column(db.Boolean, default=False)
    can_access_profile = db.Column(db.Boolean, default=True)
    can_access_outbound = db.Column(db.Boolean, default=False)
    can_access_admin_panel = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_permission(self, perm: str) -> bool:
        # الأدمن: كل شيء
        if self.is_admin:
            return True

        # perm مثل: "can_access_inbound"
        return bool(getattr(self, perm, False))

    @property
    def is_active(self) -> bool:  # type: ignore[override]
        return self.is_active_user

    def __repr__(self) -> str:
        return f"<User {self.username}>"
