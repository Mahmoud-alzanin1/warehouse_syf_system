import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user

from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

from app.core.database import db
from app.core.permissions import permission_required
from app.models.data_entry import DataEntry
from app.models.warehouse import Warehouse


# =========================
# ENV + CLOUDINARY INIT
# =========================
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

data_entry_bp = Blueprint("data_entry", __name__)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


# =========================
# UPLOAD FUNCTION
# =========================
def _save_beneficiaries_image(file_storage) -> str:
    original = file_storage.filename or ""

    _, ext = os.path.splitext(original)
    ext = ext.lower()

    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("⚠ امتداد الصورة غير مسموح (JPG/PNG/WEBP فقط)")

    # 🔥 UNIQUE FILE NAME
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:10]

    public_id = f"data_entry/{timestamp}_{unique_id}"

    try:
        result = cloudinary.uploader.upload(
            file_storage,
            public_id=public_id,
            folder="data_entry",
            overwrite=False,
            resource_type="image"
        )

        return result["secure_url"]

    except Exception as e:
        print("Cloudinary Upload Error:", e)
        raise Exception("فشل رفع الصورة إلى Cloudinary")


# =========================
# MAIN ROUTE
# =========================
@data_entry_bp.route("/", methods=["GET", "POST"])
@login_required
@permission_required("can_access_data_entry")
def index():
    warehouses = Warehouse.query.filter_by(is_active=True).all()

    if request.method == "POST":

        entry_date = request.form.get("entry_date")
        warehouse_name = request.form.get("warehouse")

        pit_account_name = request.form.get("pit_account_name")
        parcels_count = request.form.get("parcels_count") or 0
        beneficiaries_count = request.form.get("beneficiaries_count") or 0
        distribution_type = request.form.get("distribution_type")
        notes = request.form.get("notes")

        # date parse
        try:
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
        except:
            flash("تاريخ غير صحيح", "danger")
            return redirect(url_for("data_entry.index"))

        # numbers
        try:
            parcels_count = int(parcels_count)
            beneficiaries_count = int(beneficiaries_count)
        except:
            parcels_count = 0
            beneficiaries_count = 0

        # =========================
        # IMAGE UPLOAD
        # =========================
        file = request.files.get("beneficiaries_image")
        image_url = None

        if file and file.filename:
            try:
                image_url = _save_beneficiaries_image(file)
            except Exception as e:
                flash(str(e), "danger")
                return redirect(url_for("data_entry.index"))

        # save DB
        record = DataEntry(
            entry_date=entry_date,
            warehouse=warehouse_name,
            pit_account_name=pit_account_name,
            parcels_count=parcels_count,
            beneficiaries_count=beneficiaries_count,
            distribution_type=distribution_type,
            data_entry_name=current_user.username,
            notes=notes,
            beneficiaries_image=image_url,
            created_by_user_id=current_user.id,
        )

        db.session.add(record)
        db.session.commit()

        flash("✅ تم الحفظ بنجاح", "success")
        return redirect(url_for("data_entry.index"))

    # =========================
    # LIST
    # =========================
    page = request.args.get("page", 1, type=int)

    pagination = DataEntry.query.order_by(
        DataEntry.id.desc()
    ).paginate(page=page, per_page=15)

    return render_template(
        "data_entry.html",
        entries=pagination.items,
        pagination=pagination,
        warehouses=warehouses,
        filters={}
    )


# =========================
# DELETE
# =========================
@data_entry_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
@permission_required("can_access_data_entry")
def delete_entry(entry_id):
    record = DataEntry.query.get_or_404(entry_id)

    if not current_user.is_admin and record.created_by_user_id != current_user.id:
        flash("غير مسموح", "danger")
        return redirect(url_for("data_entry.index"))

    db.session.delete(record)
    db.session.commit()

    flash("🗑 تم الحذف بنجاح", "success")
    return redirect(url_for("data_entry.index"))