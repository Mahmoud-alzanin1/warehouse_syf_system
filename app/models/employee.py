from datetime import datetime
from app.core.database import db



class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)

    # أسماء بالعربي
    arabic_first_name = db.Column(db.String(100))
    arabic_second_name = db.Column(db.String(100))
    arabic_third_name = db.Column(db.String(100))
    arabic_family_name = db.Column(db.String(100))

    # أسماء بالإنجليزي
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    third_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    national_id = db.Column(db.String(9), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # "Male" / "Female"
    phone = db.Column(db.String(15), nullable=False)

    gov = db.Column(db.String(100))
    area = db.Column(db.String(100))
    street = db.Column(db.String(150))
    nearby = db.Column(db.String(150))

    education_level = db.Column(db.String(50))
    education = db.Column(db.String(100))

    hire_date = db.Column(db.Date, nullable=True)

    job_title = db.Column(db.String(100))  # "مسؤول مخزن" ... إلخ

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
