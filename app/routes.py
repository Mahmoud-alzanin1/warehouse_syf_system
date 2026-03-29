from flask import Blueprint, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    # ✅ لو مسجل دخول → ودّيه على صفحة الموظف (المسار الصحيح عندك)
    if current_user.is_authenticated:
        return redirect(url_for("users.employee_profile"))

    # ✅ لو مش مسجل → login
    return redirect(url_for("auth.login"))
