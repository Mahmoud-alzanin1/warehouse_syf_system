import os
import secrets
from datetime import datetime
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    Response,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.core.database import db
from app.models.distribution import Distribution
from app.core.permissions import permission_required


distribution_bp = Blueprint("distribution", __name__)


def _apply_filters(query, date_from_str, date_to_str, governorate, dist_point, employee_name):
    """دالة مساعدة لتطبيق الفلاتر للأدمن."""
    if date_from_str:
        try:
            d_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
            query = query.filter(Distribution.dist_date >= d_from)
        except ValueError:
            pass

    if date_to_str:
        try:
            d_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
            query = query.filter(Distribution.dist_date <= d_to)
        except ValueError:
            pass

    if governorate:
        query = query.filter(Distribution.governorate.ilike(f"%{governorate.strip()}%"))

    if dist_point:
        query = query.filter(Distribution.dist_point.ilike(f"%{dist_point.strip()}%"))

    if employee_name:
        query = query.filter(Distribution.data_entry_name.ilike(f"%{employee_name.strip()}%"))

    return query


def _get_warehouse_id_by_name(name: str):
    """يربط اسم المخزن (dist_point) بجدول warehouses ويرجع warehouse_id (fallback)."""
    if not name:
        return None
    try:
        from app.models.warehouse import Warehouse
        wh = Warehouse.query.filter_by(name=name.strip(), is_active=True).first()
        return wh.id if wh else None
    except Exception:
        return None


def _get_warehouse_name_by_id(warehouse_id: int):
    """يرجع اسم المخزن (dist_point) بناءً على warehouse_id."""
    if not warehouse_id:
        return None
    try:
        from app.models.warehouse import Warehouse
        wh = Warehouse.query.filter_by(id=warehouse_id, is_active=True).first()
        return wh.name if wh else None
    except Exception:
        return None


def _is_allowed_image(filename: str) -> bool:
    """تحقق بسيط للامتدادات المسموحة."""
    if not filename:
        return False
    _, ext = os.path.splitext(filename)
    ext = (ext or "").lower()
    return ext in {".jpg", ".jpeg", ".png", ".webp"}


@distribution_bp.route("/", methods=["GET", "POST"])
@login_required
@permission_required("can_access_distribution")
def index():
    """
    - عرض فورم التوزيع
    - حفظ بيانات توزيع جديدة
    - عرض السجلات مع الفلترة و Pagination
    - ✅ يدعم warehouse_id مباشرة + fallback من dist_point
    """

    # ========= 1) حفظ بيانات جديدة (POST) =========
    if request.method == "POST":
        dist_date_str = request.form.get("dist_date") or ""
        governorate = (request.form.get("governorate") or "").strip()
        dist_point_neighbourhood = (request.form.get("dist_point_neighbourhood") or "").strip()

        # ✅ الجديد: warehouse_id (FK) من الفورم
        warehouse_id = request.form.get("warehouse_id", type=int)

        # ✅ fallback: النص القديم
        dist_point = (request.form.get("dist_point") or "").strip()

        focal_point_name = (request.form.get("focal_point_name") or "").strip()

        beneficiaries_hhs = request.form.get("beneficiaries_hhs") or "0"
        beneficiaries_members = request.form.get("beneficiaries_members") or "0"
        nr_parcels = request.form.get("nr_parcels") or "0"

        whf_bags = request.form.get("whf_bags") or "0"
        date_bars = request.form.get("date_bars") or "0"
        heb_piece = request.form.get("heb_piece") or "0"

        add_new_item = (request.form.get("add_new_item") or "").strip()

        # أوزان الوحدات
        whf_unit_weight_kg = request.form.get("whf_unit_weight_kg") or "0"
        date_bars_unit_weight_kg = request.form.get("date_bars_unit_weight_kg") or "0"
        heb_unit_weight_kg = request.form.get("heb_unit_weight_kg") or "0"
        parcels_unit_weight_kg = request.form.get("parcels_unit_weight_kg") or "0"

        # كميات بالطن المتري (JS يحسبها ويرسلها جاهزة)
        whf_mt = request.form.get("whf_mt") or "0"
        date_bars_mt = request.form.get("date_bars_mt") or "0"
        heb_mt = request.form.get("heb_mt") or "0"
        parcels_mt = request.form.get("parcels_mt") or "0"

        # حقول الدمج المفصلة لكل صنف
        whf_damage_units = request.form.get("whf_damage_units") or "0"
        date_bars_damage_units = request.form.get("date_bars_damage_units") or "0"
        heb_damage_units = request.form.get("heb_damage_units") or "0"
        parcels_damage_units = request.form.get("parcels_damage_units") or "0"

        notes = (request.form.get("notes") or "").strip()
        data_entry_name = current_user.username

        # تحويل التاريخ
        try:
            dist_date = datetime.strptime(dist_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("تاريخ غير صالح، الرجاء اختيار تاريخ صحيح.", "danger")
            return redirect(url_for("distribution.index"))

        def to_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        def to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        beneficiaries_hhs = to_int(beneficiaries_hhs)
        beneficiaries_members = to_int(beneficiaries_members)
        nr_parcels = to_int(nr_parcels)

        whf_bags = to_int(whf_bags)
        date_bars = to_int(date_bars)
        heb_piece = to_int(heb_piece)

        whf_damage_units = to_int(whf_damage_units)
        date_bars_damage_units = to_int(date_bars_damage_units)
        heb_damage_units = to_int(heb_damage_units)
        parcels_damage_units = to_int(parcels_damage_units)

        whf_unit_weight_kg = to_float(whf_unit_weight_kg)
        date_bars_unit_weight_kg = to_float(date_bars_unit_weight_kg)
        heb_unit_weight_kg = to_float(heb_unit_weight_kg)
        parcels_unit_weight_kg = to_float(parcels_unit_weight_kg)

        whf_mt = to_float(whf_mt)
        date_bars_mt = to_float(date_bars_mt)
        heb_mt = to_float(heb_mt)
        parcels_mt = to_float(parcels_mt)

        # هل يوجد دمج؟
        is_merged = any([
            whf_damage_units,
            date_bars_damage_units,
            heb_damage_units,
            parcels_damage_units,
        ])

        # ✅ تحديد المخزن بشكل نهائي (إجباري)
        if warehouse_id:
            resolved_name = _get_warehouse_name_by_id(warehouse_id)
            if not resolved_name:
                flash("المخزن المختار غير صالح أو غير نشط.", "danger")
                return redirect(url_for("distribution.index"))
            dist_point = resolved_name
        else:
            warehouse_id = _get_warehouse_id_by_name(dist_point)

        if not warehouse_id:
            flash("الرجاء اختيار المخزن بشكل صحيح.", "danger")
            return redirect(url_for("distribution.index"))

        # حفظ صورة التوزيع (اسم فريد)
        dist_image_path = None
        file = request.files.get("dist_image")
        if file and file.filename:
            original = secure_filename(file.filename)

            if not _is_allowed_image(original):
                flash("صيغة الصورة غير مدعومة. استخدم JPG/PNG/WEBP فقط.", "danger")
                return redirect(url_for("distribution.index"))

            _, ext = os.path.splitext(original)
            ext = (ext or "").lower()

            unique_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}{ext}"

            base_upload = current_app.config.get("UPLOAD_FOLDER")
            save_dir = os.path.join(base_upload, "distribution")
            os.makedirs(save_dir, exist_ok=True)
            full_path = os.path.join(save_dir, unique_name)
            file.save(full_path)

            dist_image_path = os.path.join("distribution", unique_name).replace("\\", "/")

        record = Distribution(
            # ✅ FK للمخزن
            warehouse_id=warehouse_id,

            dist_date=dist_date,
            governorate=governorate,
            dist_point_neighbourhood=dist_point_neighbourhood,

            # ✅ نحتفظ بالاسم للعرض/التصدير
            dist_point=dist_point,

            focal_point_name=focal_point_name,

            beneficiaries_hhs=beneficiaries_hhs,
            beneficiaries_members=beneficiaries_members,
            nr_parcels=nr_parcels,

            whf_bags=whf_bags,
            date_bars=date_bars,
            heb_piece=heb_piece,

            add_new_item=add_new_item,

            whf_unit_weight_kg=whf_unit_weight_kg,
            date_bars_unit_weight_kg=date_bars_unit_weight_kg,
            heb_unit_weight_kg=heb_unit_weight_kg,
            parcels_unit_weight_kg=parcels_unit_weight_kg,

            whf_mt=whf_mt,
            date_bars_mt=date_bars_mt,
            heb_mt=heb_mt,
            parcels_mt=parcels_mt,

            whf_damage_units=whf_damage_units,
            date_bars_damage_units=date_bars_damage_units,
            heb_damage_units=heb_damage_units,
            parcels_damage_units=parcels_damage_units,

            is_merged=is_merged,
            notes=notes,
            dist_image=dist_image_path,
            data_entry_name=data_entry_name,
            created_by_user_id=current_user.id,
        )

        db.session.add(record)
        db.session.commit()

        flash("تم حفظ بيانات التوزيع.", "success")
        return redirect(url_for("distribution.index"))

    # ========= 2) عرض السجلات (GET + فلاتر + Pagination) =========
    page = request.args.get("page", 1, type=int)
    per_page = 50

    if getattr(current_user, "is_admin", False):
        date_from_str = request.args.get("date_from", "") or ""
        date_to_str = request.args.get("date_to", "") or ""
        governorate = request.args.get("governorate", "") or ""
        dist_point = request.args.get("dist_point", "") or ""
        employee_name = request.args.get("employee_name", "") or ""

        query = Distribution.query
        query = _apply_filters(query, date_from_str, date_to_str, governorate, dist_point, employee_name)
    else:
        date_from_str = ""
        date_to_str = ""
        governorate = ""
        dist_point = ""
        employee_name = ""

        query = Distribution.query.filter(Distribution.data_entry_name == current_user.username)

    pagination = query.order_by(Distribution.dist_date.desc(), Distribution.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    entries = pagination.items

    filters = {
        "date_from": date_from_str,
        "date_to": date_to_str,
        "governorate": governorate,
        "dist_point": dist_point,
        "employee_name": employee_name,
    }

    return render_template(
        "distribution.html",
        entries=entries,
        pagination=pagination,
        filters=filters,
    )


@distribution_bp.route("/export", methods=["GET"])
@login_required
@permission_required("can_access_distribution")
def export():
    """تصدير بيانات التوزيع إلى Excel"""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    if getattr(current_user, "is_admin", False):
        date_from_str = request.args.get("date_from", "") or ""
        date_to_str = request.args.get("date_to", "") or ""
        governorate = request.args.get("governorate", "") or ""
        dist_point = request.args.get("dist_point", "") or ""
        employee_name = request.args.get("employee_name", "") or ""

        query = Distribution.query
        query = _apply_filters(query, date_from_str, date_to_str, governorate, dist_point, employee_name)
    else:
        query = Distribution.query.filter(Distribution.data_entry_name == current_user.username)

    rows = query.order_by(Distribution.dist_date.asc(), Distribution.id.asc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Distribution"

    headers = [
        "Date",
        "Governorate",
        "Dist Neighbourhood",
        "Dist Point",
        "Focal Point",
        "HHs",
        "Members",
        "Nr Parcels",
        "WHF Bags",
        "Date Bars",
        "HEB Piece",
        "Add New Item",
        "WHF MT",
        "Date Bars MT",
        "HEB MT",
        "Parcels MT",
        "WHF Damage Units",
        "Date Bars Damage Units",
        "HEB Damage Units",
        "Parcels Damage Units",
        "Is Merged",
        "Notes",
        "Data Entry",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for r in rows:
        ws.append([
            r.dist_date.isoformat() if r.dist_date else "",
            r.governorate or "",
            r.dist_point_neighbourhood or "",
            r.dist_point or "",
            r.focal_point_name or "",
            r.beneficiaries_hhs or 0,
            r.beneficiaries_members or 0,
            r.nr_parcels or 0,
            r.whf_bags or 0,
            r.date_bars or 0,
            r.heb_piece or 0,
            r.add_new_item or "",
            round(r.whf_mt or 0.0, 3),
            round(r.date_bars_mt or 0.0, 3),
            round(r.heb_mt or 0.0, 3),
            round(r.parcels_mt or 0.0, 3),
            r.whf_damage_units or 0,
            r.date_bars_damage_units or 0,
            r.heb_damage_units or 0,
            r.parcels_damage_units or 0,
            "Yes" if getattr(r, "is_merged", False) else "No",
            r.notes or "",
            r.data_entry_name or "",
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@distribution_bp.route("/delete/<int:dist_id>", methods=["POST"], endpoint="delete")
@login_required
@permission_required("can_access_distribution")
def delete(dist_id):
    """حذف سجل توزيع واحد."""
    record = Distribution.query.get_or_404(dist_id)

    if not getattr(current_user, "is_admin", False):
        flash("لا تملك صلاحية حذف هذا السجل.", "danger")
        return redirect(url_for("distribution.index"))

    db.session.delete(record)
    db.session.commit()
    flash("تم حذف سجل التوزيع.", "success")
    return redirect(url_for("distribution.index"))
