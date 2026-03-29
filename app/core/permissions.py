from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

# ✅ غيره إذا بدك صفحة ثانية غير employee_profile
DEFAULT_FALLBACK_ENDPOINT = "users.employee_profile"


def permission_required(permission_name: str):
    """
    مثال:
    @permission_required("can_access_inbound")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))

            # الأدمن يدخل على الكل
            if getattr(current_user, "is_admin", False):
                return view_func(*args, **kwargs)

            # ✅ صلاحيات بوليان مباشرة
            if not current_user.has_permission(permission_name):
                flash("لا تملك صلاحية الوصول لهذه الصفحة.", "danger")
                return redirect(url_for(DEFAULT_FALLBACK_ENDPOINT))

            return view_func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    صفحات الأدمن فقط.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if not getattr(current_user, "is_admin", False) and not current_user.has_permission("can_access_admin_panel"):
            flash("لا تملك صلاحية الوصول لهذه الصفحة.", "danger")
            return redirect(url_for(DEFAULT_FALLBACK_ENDPOINT))

        return view_func(*args, **kwargs)
    return wrapper
