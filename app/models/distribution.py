from app.core.database import db
from app.core.base_model import BaseModel


class Distribution(BaseModel):
    __tablename__ = "distribution"

    # ✅ Indexes مركبة لتحسين التقارير والفلترة المشتركة
    __table_args__ = (
        # الأكثر استخداماً: تقارير حسب المخزن والتاريخ
        db.Index("ix_distribution_warehouse_date", "warehouse_id", "dist_date"),
        # تدقيق/تقارير حسب المستخدم والتاريخ
        db.Index("ix_distribution_creator_date", "created_by_user_id", "dist_date"),
    )

    id = db.Column(db.Integer, primary_key=True)

    # 🔴 مرحلة انتقالية (لو كنت تستخدم fdp سابقًا)
    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True,
        index=True
    )
    warehouse = db.relationship("Warehouse")

    # التاريخ
    dist_date = db.Column(db.Date, nullable=False, index=True)

    # معلومات الموقع
    governorate = db.Column(db.String(100), index=True)
    dist_point_neighbourhood = db.Column(db.String(150))
    dist_point = db.Column(db.String(150), index=True)
    focal_point_name = db.Column(db.String(150))

    # المستفيدين
    beneficiaries_hhs = db.Column(db.Integer, default=0)
    beneficiaries_members = db.Column(db.Integer, default=0)

    # الكميات الأساسية
    nr_parcels = db.Column(db.Integer, default=0)
    whf_bags = db.Column(db.Integer, default=0)
    date_bars = db.Column(db.Integer, default=0)
    heb_piece = db.Column(db.Integer, default=0)

    # إضافة صنف إضافي
    add_new_item = db.Column(db.String(200))
    notes = db.Column(db.Text)

    # صورة التوزيع
    dist_image = db.Column(db.String(255))
    data_entry_name = db.Column(db.String(100))

    # أوزان بالكيلو
    whf_unit_weight_kg = db.Column(db.Float, default=0.0)
    date_bars_unit_weight_kg = db.Column(db.Float, default=0.0)
    heb_unit_weight_kg = db.Column(db.Float, default=0.0)
    parcels_unit_weight_kg = db.Column(db.Float, default=0.0)

    # أوزان الطن المتري
    whf_mt = db.Column(db.Float, default=0.0)
    date_bars_mt = db.Column(db.Float, default=0.0)
    heb_mt = db.Column(db.Float, default=0.0)
    parcels_mt = db.Column(db.Float, default=0.0)

    # ✔ الدمج — مفصل لكل صنف
    whf_damage_units = db.Column(db.Integer, default=0)
    date_bars_damage_units = db.Column(db.Integer, default=0)
    heb_damage_units = db.Column(db.Integer, default=0)
    parcels_damage_units = db.Column(db.Integer, default=0)

    # هل التوزيع ناتج عن دمج؟
    is_merged = db.Column(db.Boolean, default=False, index=True)

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    def __repr__(self):
        return f"<Distribution id={self.id} merged={self.is_merged}>"
