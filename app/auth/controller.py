from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user

from app.models.user import User
from app.core.database import db
from app.users.utils import validate_password_policy  # ✅ سياسة موحّدة

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.employee_profile"))

    if request.method == "POST":
        raw_login = (request.form.get("email") or "").strip()
        password = (request.form.get("password") or "").strip()

        user = User.query.filter(
            (User.username == raw_login) | (User.email == raw_login)
        ).first()

        if not user:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")
            return render_template("login.html")

        # لو الحساب متعطل
        if not user.is_active_user:
            flash("هذا الحساب معطّل. راجع الأدمن.", "danger")
            return render_template("login.html")

        if user.check_password(password):
            login_user(user)
            return redirect(url_for("users.employee_profile"))

        flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """تسجيل الخروج وإرجاع المستخدم لصفحة تسجيل الدخول."""
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """
    تغيير كلمة المرور بشرط كلمة المرور القديمة + سياسة قوية + Logout تلقائي.
    """
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        old_password = (request.form.get("old_password") or "").strip()
        new_password = (request.form.get("new_password") or "").strip()
        confirm_password = (request.form.get("confirm_password") or "").strip()

        if not username or not old_password or not new_password or not confirm_password:
            flash("الرجاء تعبئة جميع الحقول.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("لم يتم العثور على مستخدم بهذا الاسم.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # ✅ تحقق من كلمة المرور القديمة
        if not user.check_password(old_password):
            flash("كلمة المرور القديمة غير صحيحة.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if new_password != confirm_password:
            flash("كلمتا المرور الجديدتان غير متطابقتين.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # ✅ لا تسمح أن تكون الجديدة نفس القديمة
        if user.check_password(new_password):
            flash("كلمة المرور الجديدة لا يمكن أن تكون نفس القديمة.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # ✅ سياسة كلمة مرور قوية (موحّدة من users/utils.py)
        ok, msg = validate_password_policy(new_password)
        if not ok:
            flash(msg, "danger")
            return redirect(url_for("auth.forgot_password"))

        # ✅ تحديث كلمة المرور
        user.set_password(new_password)
        db.session.commit()

        # ✅ Logout تلقائي + تنظيف الجلسة
        if current_user.is_authenticated:
            logout_user()

        flash("تم تحديث كلمة المرور بنجاح. الرجاء تسجيل الدخول مرة أخرى.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


# ✅ تم تعطيل هذا الراوت لأنه خطر (كان ينشئ أدمن بكلمة مرور ثابتة)
# إنشاء الأدمن صار فقط من ENV داخل app/__init__.py
@auth_bp.route("/create_admin")
def create_admin():
    abort(404)
