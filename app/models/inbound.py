from datetime import datetime

from app.core.database import db
from app.core.base_model import BaseModel


class Inbound(BaseModel):
    __tablename__ = "inbound"

    # ✅ Indexes مركبة (Composite) لتحسين أداء التقارير والفلترة المشتركة
    __table_args__ = (
        # الأكثر استخداماً: تقارير حسب المخزن والتاريخ
        db.Index("ix_inbound_warehouse_date", "warehouse_id", "date"),
        # فلترة حسب المخزن + تاريخ/وقت الإدخال (لأحدث الحركات)
        db.Index("ix_inbound_warehouse_datetime", "warehouse_id", "inbound_datetime"),
        # فلترة حسب المستخدم + تاريخ/وقت الإدخال (للمراجعة والتدقيق)
        db.Index("ix_inbound_creator_datetime", "created_by_user_id", "inbound_datetime"),
    )

    supervisor_name = db.Column(db.String(120), nullable=True)
    inbound_entry_name = db.Column(db.String(80), nullable=False)

    date = db.Column(db.Date, nullable=False, index=True)

    # 🔴 مرحلة انتقالية (سيُزال لاحقًا)
    fdp = db.Column(db.String(120), nullable=True, index=True)

    # ✅ الربط الحقيقي بالمخزن
    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True,
        index=True
    )
    warehouse = db.relationship("Warehouse")

    governorate = db.Column(db.String(120), nullable=True)
    waybill_number = db.Column(db.String(50), nullable=False, index=True)
    commodity = db.Column(db.String(50), nullable=True, index=True)
    si_number = db.Column(db.String(50), nullable=True)

    pallets_count = db.Column(db.Integer, nullable=True)
    units_per_pallet = db.Column(db.Integer, nullable=True)
    unit_weight_kg = db.Column(db.Float, nullable=True)
    qty_mt = db.Column(db.Float, nullable=True)
    net_boxes = db.Column(db.Integer, nullable=True)

    activity_type = db.Column(db.String(20), nullable=False, default="GFD")
    damage_count = db.Column(db.Integer, nullable=True)

    inbound_datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    movement_type = db.Column(
        db.String(20),
        nullable=False,
        default="INBOUND"
    )

    empty_pallets_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    waybill_image = db.Column(db.String(255), nullable=True)

    created_by_user_id = db.Column(db.Integer, nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<Inbound id={self.id} "
            f"waybill={self.waybill_number!r} "
            f"warehouse_id={self.warehouse_id} "
            f"date={self.date}>"
        )
