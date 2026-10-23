import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import uuid
import hashlib
import platform
import subprocess
from datetime import datetime
import urllib.request
import urllib.error

# مسار تخزين التفعيل المحلي على جهاز العميل
LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".ai_shorts_license.json")

# الرابط السحابي للوحة التحكم
REMOTE_LICENSES_URL = "https://raw.githubusercontent.com/Amino997h/shorts/v4/licenses_db.json"

def get_hwid() -> str:
    """
    استخراج بصمة فريدة لجهاز العميل (Hardware ID)
    متوافق مع Windows 10/11 الحديث بدون الحاجة لـ wmic القديم.
    """
    raw_id = ""
    try:
        if platform.system() == "Windows":
            # طريقة حديثة باستخدام powershell
            cmd = "powershell -Command \"(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID\""
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
            if output and len(output) > 5:
                raw_id = output
    except Exception:
        pass

    if not raw_id:
        # Fallback إلى المعرف الشبكي الماك أدرس
        raw_id = str(uuid.getnode())

    return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

def fetch_remote_licenses() -> dict:
    """
    جلب قاعدة بيانات المشتركين والمفاتيح لحظياً من السيرفر السحابي
    مع تجاوز الكاش (CDN Cache-Busting) والاتصال المباشر عبر GitHub API.
    """
    import base64
    import time

    # 1. الاتصال الفوري المباشر عبر GitHub Contents API (تحديث فوري 0 ثانية كاش)
    try:
        api_url = "https://api.github.com/repos/Amino997h/shorts/contents/licenses_db.json?ref=v4"
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "AIShortsAuth/1.0",
                "Accept": "application/vnd.github.v3+json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            decoded_bytes = base64.b64decode(data['content'])
            return json.loads(decoded_bytes.decode('utf-8'))
    except Exception:
        pass

    # 2. خط الدفاع الثاني: Raw URL مع طابع زمني ديناميكي لمنع كاش الخوادم
    try:
        ts_url = f"{REMOTE_LICENSES_URL}?_ts={int(time.time())}"
        req = urllib.request.Request(
            ts_url,
            headers={
                "User-Agent": "AIShortsAuth/1.0",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception:
        pass

    # 3. في حال وجود ملف محلي fallback أثناء التطوير أو انقطاع النت المؤقت
    if os.path.exists("licenses_db.json"):
        try:
            with open("licenses_db.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_local_license() -> dict:
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_local_license(key: str, client_name: str):
    data = {
        "key": key.strip(),
        "client_name": client_name,
        "hwid": get_hwid()
    }
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[AUTH] Warning: could not save local license: {e}")

def verify_license(key: str) -> tuple[bool, str, dict]:
    key = key.strip()
    if not key:
        return False, "Please enter a valid license key.", {}

    licenses = fetch_remote_licenses()
    if not licenses:
        return False, "Could not reach license server. Check your internet connection.", {}

    if key not in licenses:
        return False, "Invalid or unregistered license key.", {}

    lic_data = licenses[key]
    status = lic_data.get("status", "inactive").lower()
    client_name = lic_data.get("name", "Unknown Client")
    expires_str = lic_data.get("expires_at", "2000-01-01")
    allowed_hwid = lic_data.get("hwid", "")

    # 1. حالة التفعيل
    if status != "active":
        return False, f"Account for '{client_name}' has been disabled by admin.", lic_data

    # 2. تاريخ الانتهاء
    try:
        expires_date = datetime.strptime(expires_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if today > expires_date:
            return False, f"Subscription expired on {expires_str}. Please renew.", lic_data
    except Exception:
        return False, "Invalid license expiration date format.", lic_data

    # 3. قفل الجهاز
    current_hwid = get_hwid()
    if allowed_hwid and allowed_hwid != current_hwid:
        return False, "This license key is locked to another computer!", lic_data

    return True, f"Welcome {client_name}! Subscription active until {expires_str}.", lic_data

def check_access_or_prompt():
    print("\n=======================================================")
    print("      AI Shorts Creator - License Verification (v4)    ")
    print("=======================================================")

    local_data = load_local_license()
    saved_key = local_data.get("key", "")

    if saved_key:
        valid, msg, lic_data = verify_license(saved_key)
        if valid:
            print(f"[OK] {msg}")
            print(f"[OK] Machine HWID: {get_hwid()}\n")
            return True
        else:
            print(f"[X] License issue: {msg}")

    print(f"\n[!] Machine HWID: {get_hwid()}")
    print("[!] Please enter your License Key to activate:")
    
    while True:
        try:
            key_input = input("Enter Key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nActivation cancelled. Exiting...")
            sys.exit(1)

        valid, msg, lic_data = verify_license(key_input)
        if valid:
            print(f"\n[OK] Success! {msg}")
            save_local_license(key_input, lic_data.get("name", "User"))
            return True
        else:
            print(f"\n[X] Activation failed: {msg}")
            print("Please try again or contact support.\n")

if __name__ == "__main__":
    check_access_or_prompt()
