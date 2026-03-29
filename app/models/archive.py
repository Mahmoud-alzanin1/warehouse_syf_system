from app.core.database import db
from app.core.base_model import BaseModel

class Archive(BaseModel):
    __tablename__ = "archive"

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
