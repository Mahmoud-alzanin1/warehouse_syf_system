from app.core.database import db
from app.core.base_model import BaseModel


class Inventory(BaseModel):
    __tablename__ = "inventory"

    # ✅ يمنع تكرار نفس المنتج داخل نفس المخزن
    __table_args__ = (
        db.UniqueConstraint("warehouse_id", "product_id", name="uq_inventory_warehouse_product"),
        db.Index("ix_inventory_warehouse_product", "warehouse_id", "product_id"),
    )

    warehouse_id = db.Column(
        db.Integer,
        db.ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    quantity = db.Column(db.Integer, default=0)
