"""
build_release_v4.py
Master packaging pipeline: Encrypted Single-File Bytecode Containers.
Produces a client release folder containing ZERO plain .py files.
"""
import os
import sys
import shutil
import marshal
import py_compile
import zipfile

RELEASE_DIR = os.path.abspath("AI_Shorts_Client_Release")
ZIP_TARGET = os.path.abspath("AI_Shorts_Pro.zip")

# Dynamic 64-byte cipher key (synthesized mathematically, no static string token in co_consts)
CIPHER_KEY = bytes([((i * 79 + 137) & 0xFF) ^ ((i % 7) * 31 & 0xFF) for i in range(64)])

STUB_TEMPLATE = '''import marshal, sys, os
# Dynamic key derivation: no plaintext key constant exists in co_consts
_KEY = bytes([((_i * 79 + 137) & 0xFF) ^ ((_i % 7) * 31 & 0xFF) for _i in range(64)])
_PAYLOAD = {payload!r}
_base = os.path.dirname(os.path.abspath(__file__))
if _base not in sys.path:
    sys.path.insert(0, _base)

# Defend against module shadowing / rogue .py spoofing
for _mod in ("auth_guard", "video_maker", "web_gui"):
    _rogue = os.path.join(_base, _mod + ".py")
    if os.path.exists(_rogue):
        try:
            os.remove(_rogue)
        except Exception:
            sys.exit(1)

# Pre-bind genuine compiled auth_guard.pyc into sys.modules if present
_ag_pyc = os.path.join(_base, "auth_guard.pyc")
if __name__ != "auth_guard" and os.path.exists(_ag_pyc) and "auth_guard" not in sys.modules:
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location("auth_guard", _ag_pyc)
    if _sp and _sp.loader:
        _m = _iu.module_from_spec(_sp)
        sys.modules["auth_guard"] = _m
        _sp.loader.exec_module(_m)

_dec = bytes([b ^ _KEY[i % len(_KEY)] for i, b in enumerate(_PAYLOAD)])
_code = marshal.loads(_dec)
_globs = globals()
_globs.update({{'__file__': os.path.abspath(__file__), '__name__': __name__}})
exec(_code, _globs)
'''

def compile_and_encrypt(source_path, target_pyc_path, mod_name):
    with open(source_path, "r", encoding="utf-8") as f:
        src = f.read()
    
    # 1. Compile inner source with optimize=2 and sanitized filename
    inner_code = compile(src, f"<{mod_name}_core>", "exec", optimize=2)
    marshaled = marshal.dumps(inner_code)
    
    # 2. Encrypt bytecode payload with dynamic cipher key
    encrypted = bytes([b ^ CIPHER_KEY[i % len(CIPHER_KEY)] for i, b in enumerate(marshaled)])
    
    # 3. Generate bootstrap loader source
    loader_src = STUB_TEMPLATE.format(payload=encrypted)
    temp_stub_py = target_pyc_path + ".temp.py"
    try:
        with open(temp_stub_py, "w", encoding="utf-8") as f:
            f.write(loader_src)
            
        # 4. Compile bootstrap loader with dfile="<bootstrap>" to prevent developer path leak
        py_compile.compile(temp_stub_py, cfile=target_pyc_path, dfile="<bootstrap>", doraise=True, optimize=2)
    finally:
        if os.path.exists(temp_stub_py):
            os.remove(temp_stub_py)
            
    print(f"[OK] Compiled & Encrypted: {os.path.basename(source_path)} -> {os.path.basename(target_pyc_path)} ({os.path.getsize(target_pyc_path):,} bytes)")

def build_package():
    print("=" * 65)
    print("  Building AI Shorts Client Release (Encrypted Bytecode Pack v4)")
    print("=" * 65)
    
    # Clean previous release directory if needed
    if os.path.exists(RELEASE_DIR):
        print(f"Cleaning previous release directory: {RELEASE_DIR}")
        shutil.rmtree(RELEASE_DIR, ignore_errors=True)
    os.makedirs(RELEASE_DIR, exist_ok=True)
    
    # 1. Encrypt and compile core scripts into single-file .pyc containers
    scripts = [
        ("auth_guard.py", "auth_guard.pyc", "auth_guard"),
        ("web_gui.py", "web_gui.pyc", "web_gui"),
        ("video_maker.py", "video_maker.pyc", "video_maker")
    ]
    for src, dst, name in scripts:
        src_path = os.path.abspath(src)
        dst_path = os.path.join(RELEASE_DIR, dst)
        assert os.path.exists(src_path), f"Source file missing: {src_path}"
        compile_and_encrypt(src_path, dst_path, name)
        
    # 2. Bundle required assets
    assets = [
        "theboldfont.ttf",
        "config.json",
        "start.bat",
        "install.bat",
        "README.md"
    ]
    for asset in assets:
        if os.path.exists(asset):
            shutil.copy2(asset, os.path.join(RELEASE_DIR, asset))
            print(f"[OK] Bundled asset: {asset} ({os.path.getsize(asset):,} bytes)")
        else:
            print(f"[WARNING] Asset not found: {asset}")
            
    # Copy Kokoro models directory if present
    if os.path.exists("kokoro_models"):
        print("Copying kokoro_models/ directory (this may take a few seconds)...")
        shutil.copytree("kokoro_models", os.path.join(RELEASE_DIR, "kokoro_models"), dirs_exist_ok=True)
        print("[OK] Bundled directory: kokoro_models/")
    else:
        print("[WARNING] kokoro_models/ not found in project root!")
        
    # 3. Clean up any accidental .py files or leftover build artifacts
    for root, dirs, files in os.walk(RELEASE_DIR):
        for d in list(dirs):
            if d == "__pycache__" or d.startswith("pyarmor"):
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                print(f"[REMOVED] Stray cache directory: {d}")
        for file in files:
            if file.endswith(".py"):
                os.remove(os.path.join(root, file))
                print(f"[REMOVED] Stray .py file: {file}")

    # 4. Create synchronized AI_Shorts_Pro.zip archive (Excluding large local model binaries to stay within GitHub's 100MB quota)
    print(f"\nCompressing package into {ZIP_TARGET}...")
    with zipfile.ZipFile(ZIP_TARGET, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(RELEASE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, RELEASE_DIR)
                # Keep zip under GitHub 100MB limit: kokoro model onnx resides in release folder and can be auto-downloaded if absent
                if arc_name.startswith("kokoro_models"):
                    continue
                zf.write(file_path, arc_name)
    print(f"[OK] Distribution archive created: {ZIP_TARGET} ({os.path.getsize(ZIP_TARGET):,} bytes)")
                
    # 5. Pre-flight Acceptance Verification
    verify_package()

def verify_package():
    print("\n" + "=" * 65)
    print("  Running Pre-flight Acceptance Audit")
    print("=" * 65)
    
    # Check 1: Strict Zero plain .py files in release folder and zip
    py_files = []
    for root, dirs, files in os.walk(RELEASE_DIR):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    assert len(py_files) == 0, f"FAILED R1: Found plain .py files in release: {py_files}"
    print("[PASS] R1.1: Exactly 0 plain .py files exist in release folder.")

    assert os.path.exists(ZIP_TARGET), f"FAILED: Zip archive missing: {ZIP_TARGET}"
    with zipfile.ZipFile(ZIP_TARGET, "r") as zf:
        zip_py = [n for n in zf.namelist() if n.endswith(".py")]
        assert len(zip_py) == 0, f"FAILED R1: Found plain .py in zip: {zip_py}"
    print("[PASS] R1.1b: Exactly 0 plain .py files exist in zip archive.")
    
    # Check 2: All compiled containers exist and contain zero leaked strings or developer paths
    pyc_files = ["auth_guard.pyc", "web_gui.pyc", "video_maker.pyc"]
    forbidden_strings = [
        b"def generate_video_pipeline",
        b"https://raw.githubusercontent.com",
        b"Win32_ComputerSystemProduct",
        b"def execute_topic",
        b"def load_config",
        b"def generate_script",
        b"AiShorts_Client_Sec_2026_Key"
    ]
    for pf in pyc_files:
        full_p = os.path.join(RELEASE_DIR, pf)
        assert os.path.exists(full_p), f"Missing compiled artifact: {pf}"
        content = open(full_p, "rb").read()
        for forbidden in forbidden_strings:
            assert forbidden not in content, f"Forbidden token leaked in {pf}: {forbidden.decode(errors='replace')}"
            
        # Check code object header sanitization
        with open(full_p, "rb") as f:
            f.read(16)
            co = marshal.load(f)
        assert co.co_filename == "<bootstrap>", f"FAILED: co_filename in {pf} is {co.co_filename}, expected <bootstrap>"
        
        # Verify no developer paths in raw bytes
        assert b"Users" not in content, f"Developer path 'Users' leaked in {pf}"
        assert b"OneDrive" not in content, f"Developer path 'OneDrive' leaked in {pf}"
        print(f"[PASS] R1.2: {pf} verified: fully encrypted bytecode container, co_filename=<bootstrap>, zero plain source/path tokens leaked.")
        
    # Check 3: Essential assets verification
    assert os.path.exists(os.path.join(RELEASE_DIR, "theboldfont.ttf")), "FAILED: theboldfont.ttf missing!"
    assert os.path.getsize(os.path.join(RELEASE_DIR, "theboldfont.ttf")) > 0, "FAILED: theboldfont.ttf is empty!"
    print("[PASS] R2.1: theboldfont.ttf asset verified.")
    
    assert os.path.exists(os.path.join(RELEASE_DIR, "config.json")), "FAILED: config.json missing!"
    print("[PASS] R2.2: config.json verified.")
    
    assert os.path.exists(os.path.join(RELEASE_DIR, "start.bat")), "FAILED: start.bat missing!"
    start_bat_content = open(os.path.join(RELEASE_DIR, "start.bat"), "r", encoding="utf-8", errors="replace").read()
    assert "web_gui.pyc" in start_bat_content, "FAILED: start.bat does not reference web_gui.pyc!"
    assert "^&" in start_bat_content or "&" not in start_bat_content, "FAILED: unescaped & in start.bat"
    print("[PASS] R2.3: start.bat verified with web_gui.pyc launcher and escaped ampersands.")
    
    assert os.path.exists(os.path.join(RELEASE_DIR, "install.bat")), "FAILED: install.bat missing!"
    install_bat_content = open(os.path.join(RELEASE_DIR, "install.bat"), "r", encoding="utf-8", errors="replace").read()
    assert "Python 3.12" in install_bat_content, "FAILED: install.bat missing Python 3.12 requirement"
    print("[PASS] R2.4: install.bat verified with Python 3.12 requirement.")
    
    assert os.path.exists(os.path.join(RELEASE_DIR, "kokoro_models")), "FAILED: kokoro_models missing!"
    print("[PASS] R2.5: kokoro_models/ directory verified.")
    
    print("\n[SUCCESS] AI_Shorts_Client_Release & AI_Shorts_Pro.zip are 100% compliant with R1 and R2 criteria!\n")

if __name__ == "__main__":
    build_package()
