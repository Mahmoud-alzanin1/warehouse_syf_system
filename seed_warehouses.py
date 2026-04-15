from app import create_app
from app.core.database import db
from app.models.warehouse import Warehouse

WAREHOUSES = [
    "SYF-Abu Rashid",
    "FPDSYFS17",
    "AL-Migdad",
    "Abu Zayed Store",
    "Al-Zawaida Club SYFS",
]

def seed():
    app = create_app()

    with app.app_context():

        # 🔥 تأكد من إنشاء الجداول
        db.create_all()

        added = 0

        for name in WAREHOUSES:
            name = name.strip()

            exists = Warehouse.query.filter_by(name=name).first()

            if not exists:
                db.session.add(
                    Warehouse(
                        name=name,
                        is_active=True
                    )
                )
                added += 1

        db.session.commit()

        print(f"✅ Warehouses seeded successfully. Added: {added}")


if __name__ == "__main__":
    seed()