import re

def validate_password_policy(password: str):
    """
    سياسة كلمة مرور موحّدة لكل المشروع:
    - 8 حرف على الأقل
    - حرف كبير
    - حرف صغير
    - رقم
    - رمز خاص
    - بدون فراغات
    """

    if len(password) < 8:
        return False, "كلمة السر يجب أن تكون 8 حرف على الأقل."

    if " " in password:
        return False, "كلمة السر لا يجب أن تحتوي على فراغات."

    if not re.search(r"[A-Z]", password):
        return False, "كلمة السر يجب أن تحتوي على حرف كبير (A-Z)."

    if not re.search(r"[a-z]", password):
        return False, "كلمة السر يجب أن تحتوي على حرف صغير (a-z)."

    if not re.search(r"[0-9]", password):
        return False, "كلمة السر يجب أن تحتوي على رقم (0-9)."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "كلمة السر يجب أن تحتوي على رمز خاص مثل (!@#$%)."

    return True, ""
