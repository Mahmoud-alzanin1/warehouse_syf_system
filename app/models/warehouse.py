from datetime import datetime
from app.core.database import db


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    # ✅ Index مركب لتحسين قائمة المخازن النشطة (شائع جداً في الـ dropdowns)
    __table_args__ = (
        db.Index("ix_warehouses_active_name", "is_active", "name"),
    )

    id = db.Column(db.Integer, primary_key=True)

    # اسم المخزن/نقطة التوزيع (لازم يكون Unique عشان الربط بالاسم)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)

    # للتفعيل/الإيقاف
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # وقت الإنشاء
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    def __repr__(self):
        return f"<Warehouse {self.id} {self.name}>"
