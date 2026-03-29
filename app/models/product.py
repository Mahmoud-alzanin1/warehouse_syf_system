from app.core.database import db
from app.core.base_model import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    # ✅ المنتج صار عام (مش مربوط بمخزن)
    # نضيف index على الاسم لأنه البحث بالاسم شائع
    name = db.Column(db.String(100), nullable=False, index=True)

    description = db.Column(db.String(255))
    price = db.Column(db.Float)
