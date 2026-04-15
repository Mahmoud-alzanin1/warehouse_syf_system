from app import create_app, db
from app.models.user import User
from app.models.warehouse import Warehouse

app = create_app()

WAREHOUSES = [
    "SYF-Abu Rashid",
    "FPDSYFS17",
    "AL-Migdad",
    "Abu Zayed Store",
    "Al-Zawaida Club SYFS",
]

ADMIN_USERNAME = "mahmoud"
ADMIN_EMAIL = "mahmoud@example.com"
ADMIN_PASSWORD = "Mahmoud123*"

with app.app_context():

    # ================= ADMIN =================
    admin = User.query.filter_by(username=ADMIN_USERNAME).first()

    if not admin:
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            role="admin",
            is_admin=True,
            is_active_user=True,
            can_access_inbound=True,
            can_access_distribution=True,
            can_access_data_entry=True,
            can_access_dashboard=True,
            can_access_profile=True,
            can_access_outbound=True,
            can_access_admin_panel=True,
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        print("✅ Admin created")
    else:
        print("ℹ️ Admin already exists")

    # ================= WAREHOUSES =================
    added = 0

    for name in WAREHOUSES:
        exists = Warehouse.query.filter_by(name=name).first()
        if not exists:
            db.session.add(Warehouse(name=name, is_active=True))
            added += 1

    print(f"✅ Warehouses added: {added}")

    db.session.commit()