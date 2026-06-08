"""Production Health Check - v1.37.0.

Verifies:
1. Critical binaries (ffmpeg, fluidsynth).
2. Python dependency availability.
3. Submodule state.
"""

import subprocess
import shutil
import sys
import os

def check_binary(name):
    path = shutil.which(name)
    if path:
        print(f"[OK] {name} found at {path}")
        return True
    else:
        print(f"[FAIL] {name} NOT FOUND")
        return False

def check_python_module(name):
    try:
        __import__(name)
        print(f"[OK] Python module '{name}' is available")
        return True
    except ImportError:
        print(f"[FAIL] Python module '{name}' NOT FOUND")
        return False

def run_health_check():
    print("--- Hymnmania Health Check ---")

    binaries = ["ffmpeg", "fluidsynth", "basic-pitch"]
    modules = ["mido", "librosa", "torch", "transformers", "diffusers", "requests_oauthlib", "live", "flask"]

    all_ok = True

    print("\nChecking Binaries:")
    for b in binaries:
        if not check_binary(b): all_ok = False

    print("\nChecking Python Modules:")
    for m in modules:
        if not check_python_module(m): all_ok = False

    print("\nChecking Project Structure:")
    if os.path.exists("submodules/ableton_psytrance_hymn_creator"):
        print("[OK] Submodule 'ableton_psytrance_hymn_creator' is present")
    else:
        print("[FAIL] Submodule 'ableton_psytrance_hymn_creator' is MISSING")
        all_ok = False

    if all_ok:
        print("\nSYSTEM HEALTHY. Ready for production.")
        return 0
    else:
        print("\nSYSTEM UNHEALTHY. Check failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_health_check())
