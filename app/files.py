import os
from flask import Blueprint, current_app, abort, send_from_directory
from flask_login import login_required

files_bp = Blueprint("files", __name__, url_prefix="/files")


@files_bp.route("/<path:path>")
@login_required
def serve_upload(path: str):
    """
    Serve uploaded files stored under instance/uploads (UPLOAD_ROOT).

    Supports these DB formats:
      - uploads/waybills/xxx.png
      - waybills/xxx.png
      - uploads/beneficiaries/xxx.png
      - beneficiaries/xxx.png

    Example URL:
      /files/uploads/waybills/xxx.png
      /files/waybills/xxx.png
    """
    upload_root = current_app.config.get("UPLOAD_ROOT")
    if not upload_root:
        abort(404)

    norm = (path or "").replace("\\", "/").strip()
    if not norm:
        abort(404)

    # ✅ allow both with/without "uploads/"
    if norm.startswith("uploads/"):
        rel = norm[len("uploads/"):]
    else:
        rel = norm

    # ✅ normalize & prevent traversal
    rel = os.path.normpath(rel).replace("\\", "/")
    if rel.startswith("../") or rel.startswith("..") or "/../" in rel:
        abort(403)

    # ✅ ensure inside upload_root
    base = os.path.abspath(upload_root)
    full = os.path.abspath(os.path.join(base, rel))
    if not full.startswith(base + os.sep) and full != base:
        abort(403)

    if not os.path.isfile(full):
        abort(404)

    # send_from_directory expects:
    # - directory: base folder
    # - path: relative path inside directory (can include subfolders)
    return send_from_directory(base, rel, as_attachment=False)
