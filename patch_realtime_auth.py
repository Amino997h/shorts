with open("auth_guard.py", "r", encoding="utf-8") as f:
    code = f.read()

import re

pattern = r"def fetch_remote_licenses\(\) -> dict:.*?return \{\}"
replacement = '''def fetch_remote_licenses() -> dict:
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
    return {}'''

new_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
with open("auth_guard.py", "w", encoding="utf-8") as f:
    f.write(new_code)

print("SUCCESSFULLY PATCHED")
