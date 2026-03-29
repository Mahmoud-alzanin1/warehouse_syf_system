from datetime import datetime
import re

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user

from app.core.database import db
from app.models.employee import Employee
from app.users.utils import validate_password_policy


# ✅ لازم يكون موجود بهذا الاسم (عشان __init__.py يستورده)
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def employee_profile():
    """
    Employee Profile
    GET  => عرض الفورم
    POST => حفظ البيانات
    """

    employee = Employee.query.filter_by(created_by_user_id=current_user.id).first()

    if request.method == "POST":
        form = request.form

        # إنشاء سجل أول مرة
        if employee is None:
            employee = Employee(created_by_user_id=current_user.id)
            db.session.add(employee)

        # ✅ Required fields (عشان ما يطلع IntegrityError)
        national_id = (form.get("national_id") or "").strip()
        dob_str = (form.get("dob") or "").strip()
        gender = (form.get("gender") or "").strip()
        phone = (form.get("phone") or "").strip()

        # بدل ما يطلع Error من DB، نعطي رسائل واضحة
        if not national_id:
            flash("الرجاء تعبئة حقل رقم الهوية.", "danger")
            return redirect(url_for("users.employee_profile"))

        if not re.fullmatch(r"\d{9}", national_id):
            flash("رقم الهوية يجب أن يكون 9 أرقام.", "danger")
            return redirect(url_for("users.employee_profile"))

        if not dob_str:
            flash("الرجاء تعبئة حقل تاريخ الميلاد.", "danger")
            return redirect(url_for("users.employee_profile"))

        if gender not in ("Male", "Female"):
            flash("الرجاء اختيار الجنس.", "danger")
            return redirect(url_for("users.employee_profile"))

        if not phone:
            flash("الرجاء تعبئة رقم الجوال.", "danger")
            return redirect(url_for("users.employee_profile"))

        # ===================
        # Save fields
        # ===================

        # عربي
        employee.arabic_first_name = (form.get("arabic_first_name") or "").strip() or None
        employee.arabic_second_name = (form.get("arabic_second_name") or "").strip() or None
        employee.arabic_third_name = (form.get("arabic_third_name") or "").strip() or None
        employee.arabic_family_name = (form.get("arabic_family_name") or "").strip() or None

        # English
        employee.first_name = (form.get("first_name") or "").strip() or None
        employee.second_name = (form.get("second_name") or "").strip() or None
        employee.third_name = (form.get("third_name") or "").strip() or None
        employee.last_name = (form.get("last_name") or "").strip() or None

        # Required
        employee.national_id = national_id
        employee.gender = gender
        employee.phone = phone

        # dob parse
        try:
            employee.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            flash("صيغة تاريخ الميلاد غير صحيحة.", "danger")
            return redirect(url_for("users.employee_profile"))

        # Address
        employee.gov = (form.get("gov") or "").strip() or None
        employee.area = (form.get("area") or "").strip() or None
        employee.street = (form.get("street") or "").strip() or None
        employee.nearby = (form.get("nearby") or "").strip() or None

        # Education
        employee.education_level = (form.get("education_level") or "").strip() or None
        employee.education = (form.get("education") or "").strip() or None

        # Hire date
        hire_str = (form.get("hire_date") or "").strip()
        if hire_str:
            try:
                employee.hire_date = datetime.strptime(hire_str, "%Y-%m-%d").date()
            except ValueError:
                flash("صيغة تاريخ التعيين غير صحيحة.", "danger")
                return redirect(url_for("users.employee_profile"))
        else:
            employee.hire_date = None

        # Job title
        employee.job_title = (form.get("job_title") or "").strip() or None

        db.session.commit()
        flash("تم حفظ بيانات الموظف بنجاح ✅", "success")
        return redirect(url_for("users.employee_profile"))

    # ✅ GET
    return render_template("employee_profile.html", employee=employee, active_page="employee")


@users_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = (request.form.get("old_password") or "").strip()
        new_password = (request.form.get("new_password") or "").strip()
        confirm_password = (request.form.get("confirm_password") or "").strip()

        if not old_password or not new_password or not confirm_password:
            flash("جميع الحقول مطلوبة.", "danger")
            return redirect(url_for("users.change_password"))

        if not current_user.check_password(old_password):
            flash("كلمة السر القديمة غير صحيحة.", "danger")
            return redirect(url_for("users.change_password"))

        if new_password != confirm_password:
            flash("كلمة السر الجديدة غير متطابقة.", "danger")
            return redirect(url_for("users.change_password"))

        if current_user.check_password(new_password):
            flash("لا يمكن استخدام نفس كلمة السر القديمة.", "warning")
            return redirect(url_for("users.change_password"))

        ok, msg = validate_password_policy(new_password)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for("users.change_password"))

        current_user.set_password(new_password)
        db.session.commit()

        logout_user()
        flash("تم تغيير كلمة السر بنجاح ✅ الرجاء تسجيل الدخول مرة أخرى.", "success")
        return redirect(url_for("auth.login"))

    return render_template("change_password.html", active_page="change_password")
