from datetime import datetime
from app.core.database import db


class Outbound(db.Model):
    __tablename__ = "outbound"

    # ✅ Indexes مركبة لتحسين التقارير والفلترة المشتركة
    __table_args__ = (
        # الأكثر استخداماً: تقارير حسب المخزن والتاريخ
        db.Index("ix_outbound_warehouse_date", "warehouse_id", "date"),
        # فلترة حسب المخزن + تاريخ/وقت الإدخال (لأحدث الحركات)
        db.Index("ix_outbound_warehouse_datetime", "warehouse_id", "outbound_datetime"),
        # فلترة حسب المستخدم + تاريخ/وقت الإدخال (للمراجعة والتدقيق)
        db.Index("ix_outbound_creator_datetime", "created_by_user_id", "outbound_datetime"),
    )

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, nullable=False, index=True)

    # 🔴 مرحلة انتقالية
    fdp = db.Column(db.String(128), nullable=False, index=True)

    # ✅ الربط الحقيقي
    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True,
        index=True
    )
    warehouse = db.relationship("Warehouse")

    governorate = db.Column(db.String(128), nullable=True)

    waybill_number = db.Column(db.String(64), nullable=False, index=True)
    commodity = db.Column(db.String(32), nullable=False, index=True)
    si_number = db.Column(db.String(64), nullable=True)

    pallets_count = db.Column(db.Integer, default=0)
    empty_pallets = db.Column(db.Integer, default=0)
    units_per_pallet = db.Column(db.Integer, default=0)

    net_boxes = db.Column(db.Integer, default=0)
    unit_weight_kg = db.Column(db.Float, default=0.0)
    qty_mt = db.Column(db.Float, default=0.0)

    damage_count = db.Column(db.Integer, default=0)

    activity_type = db.Column(db.String(64), default="Outbound Dispatch")
    supervisor_name = db.Column(db.String(128))
    outbound_entry_name = db.Column(db.String(128))

    outbound_datetime = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    waybill_image = db.Column(db.String(255))

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
