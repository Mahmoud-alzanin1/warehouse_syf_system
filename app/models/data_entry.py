from app.core.database import db
from app.core.base_model import BaseModel


class DataEntry(BaseModel):
    __tablename__ = "data_entries"

    # ✅ Indexes مركبة لتحسين التقارير والفلترة المشتركة
    __table_args__ = (
        # تقارير حسب المخزن والتاريخ
        db.Index("ix_dataentry_warehouse_date", "warehouse_id", "entry_date"),
        # تدقيق حسب المستخدم والتاريخ
        db.Index("ix_dataentry_creator_date", "created_by_user_id", "entry_date"),
    )

    # تاريخ الإدخال
    entry_date = db.Column(db.Date, nullable=False, index=True)

    # اسم المخزن (نخليه كنص عشان القوالب/التصدير ما ينكسروا)
    warehouse = db.Column(db.String(150), nullable=True, index=True)

    # ✅ FK للمخزن الحقيقي
    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=True,
        index=True,
    )

    # (اختياري) علاقة لو احتجتها لاحقاً بالداشبورد
    warehouse_rel = db.relationship("Warehouse", backref="data_entries")

    # اسم حساب PIT
    pit_account_name = db.Column(db.String(150), nullable=True, index=True)

    # عدد الطرود الموزعة
    parcels_count = db.Column(db.Integer, default=0)

    # عدد المستفيدين
    beneficiaries_count = db.Column(db.Integer, default=0)

    # نوع التوزيع
    distribution_type = db.Column(db.String(50), nullable=True, index=True)

    # اسم موظف الداتا انتري
    data_entry_name = db.Column(db.String(150), nullable=True)

    # ملاحظات
    notes = db.Column(db.String(255), nullable=True)

    # صورة للمستفيدين
    beneficiaries_image = db.Column(db.String(255), nullable=True)

    # المستخدم الذي أدخل السجل
    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
