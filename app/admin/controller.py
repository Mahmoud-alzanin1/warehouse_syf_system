from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user

from app.core.database import db
from app.models.user import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ==========================
# Decorator: الأدمن فقط
# ==========================
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("الرجاء تسجيل الدخول أولاً.", "danger")
            return redirect(url_for("auth.login"))

        if not getattr(current_user, "is_admin", False):
            flash("لا تملك صلاحية الدخول إلى لوحة التحكم.", "danger")
            return redirect(url_for("users.employee_profile"))

        return func(*args, **kwargs)

    return wrapper


# ==========================
# Decorator عام للصلاحيات
# ==========================
def permission_required(permission_name: str):
    """
    permission_name: اسم خاصية في User
    مثل: can_access_inbound, can_access_distribution, ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = current_user

            if not user.is_authenticated:
                flash("الرجاء تسجيل الدخول.", "danger")
                return redirect(url_for("auth.login"))

            # لو الحساب متعطل
            if not getattr(user, "is_active_user", True):
                flash("🚫 تم تعطيل حسابك من قبل المدير.", "danger")
                return redirect(url_for("auth.login"))

            # الأدمن يدخل كل شيء
            if getattr(user, "is_admin", False):
                return func(*args, **kwargs)

            # فحص وجود الخاصية + قيمتها
            if not getattr(user, permission_name, False):
                flash("⛔ لا تملك صلاحية لفتح هذه الصفحة.", "danger")
                return redirect(url_for("users.employee_profile"))

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ==========================
# صفحة إدارة المستخدمين
# ==========================
@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def users_page():
    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin/users_manage.html", users=users)


# ==========================
# إنشاء مستخدم جديد من لوحة الأدمن
# ==========================
@admin_bp.route("/users/create", methods=["POST"])
@login_required
@admin_required
def create_user():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not username or not password:
        flash("اسم المستخدم وكلمة السر مطلوبان.", "danger")
        return redirect(url_for("admin.users_page"))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("اسم المستخدم مستخدم مسبقًا.", "danger")
        return redirect(url_for("admin.users_page"))

    new_user = User(
        username=username,
        email=email or None,
        is_admin=False,
        role="user",
        is_active_user=True,  # يفضل تجعلها True افتراضيًا
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    flash("✅ تم إنشاء المستخدم بنجاح.", "success")
    return redirect(url_for("admin.users_page"))


# ==========================
# تفعيل / تعطيل مستخدم
# ==========================
@admin_bp.route("/users/toggle/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    # لا نسمح بتعطيل الأدمن الرئيسي مثلاً
    if user.username == "mahmoud":
        flash("لا يمكن تعطيل المستخدم الرئيسي.", "danger")
        return redirect(url_for("admin.users_page"))

    user.is_active_user = not user.is_active_user
    db.session.commit()

    flash("تم تغيير حالة المستخدم.", "success")
    return redirect(url_for("admin.users_page"))


# ==========================
# حذف مستخدم
# ==========================
@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == "mahmoud":
        flash("لا يمكن حذف المستخدم الرئيسي.", "danger")
        return redirect(url_for("admin.users_page"))

    db.session.delete(user)
    db.session.commit()

    flash("تم حذف المستخدم.", "success")
    return redirect(url_for("admin.users_page"))


# ==========================
# تحديث صلاحيات مستخدم
# ==========================
@admin_bp.route("/users/permissions/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def update_permissions(user_id):
    user = User.query.get_or_404(user_id)

    user.can_access_inbound      = "inbound" in request.form
    user.can_access_distribution = "distribution" in request.form
    user.can_access_data_entry   = "data_entry" in request.form
    user.can_access_dashboard    = "dashboard" in request.form
    user.can_access_profile      = "profile" in request.form
    user.can_access_outbound = "outbound" in request.form
    
    db.session.commit()
    flash("✔ تم تحديث صلاحيات المستخدم.", "success")
    return redirect(url_for("admin.users_page"))
