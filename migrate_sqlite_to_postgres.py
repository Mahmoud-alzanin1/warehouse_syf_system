from app import create_app, db
from app.models.user import User
from app.models.warehouse import Warehouse

app = create_app()

def migrate():
    with app.app_context():

        print("🚀 Starting migration...")

        # ---------------- USERS ----------------
        users = User.query.all()
        print(f"Found {len(users)} users")

        for u in users:

            exists = User.query.filter_by(username=u.username).first()
            if exists:
                print(f"⏩ Skipping existing user: {u.username}")
                continue

            new_user = User(
                username=u.username,
                email=u.email,
                password_hash=u.password_hash,
                role=u.role,
                is_admin=u.is_admin,
                is_active_user=u.is_active_user,
                can_access_inbound=u.can_access_inbound,
                can_access_distribution=u.can_access_distribution,
                can_access_data_entry=u.can_access_data_entry,
                can_access_dashboard=u.can_access_dashboard,
                can_access_profile=u.can_access_profile,
                can_access_outbound=u.can_access_outbound,
                can_access_admin_panel=u.can_access_admin_panel,
            )

            db.session.add(new_user)

        # ---------------- WAREHOUSES ----------------
        warehouses = Warehouse.query.all()
        print(f"Found {len(warehouses)} warehouses")

        for w in warehouses:

            exists_w = Warehouse.query.filter_by(name=w.name).first()
            if exists_w:
                print(f"⏩ Skipping warehouse: {w.name}")
                continue

            new_w = Warehouse(
                name=w.name,
                is_active=w.is_active
            )

            db.session.add(new_w)

        # ---------------- COMMIT ----------------
        db.session.commit()

        print("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()