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
        for name in WAREHOUSES:
            name = name.strip()
            exists = Warehouse.query.filter_by(name=name).first()
            if not exists:
                db.session.add(Warehouse(name=name, is_active=True))

        db.session.commit()
        print("✅ Warehouses seeded successfully.")


if __name__ == "__main__":
    seed()
