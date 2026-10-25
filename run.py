#!/usr/bin/env python
"""
PfunzoBridge Mobile App Launcher.
Starts the server accessible on both localhost and local mobile devices via WiFi.
"""
import os
import sys
from pathlib import Path
import subprocess

# Ensure local site-packages are on sys.path
USER_PACKAGES = [
    Path(r"C:\Users\Ipfi\AppData\Local\Programs\Python\Python314\Lib\site-packages"),
    Path(os.path.expanduser(r"~\AppData\Local\Programs\Python\Python314\Lib\site-packages")),
    Path(os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")),
]
for pkg in USER_PACKAGES:
    if pkg.exists() and str(pkg) not in sys.path:
        sys.path.insert(0, str(pkg))

def main():
    print("=" * 65)
    print("  🇿🇦 PfunzoBridge - Access to Higher Education Platform")
    print("  FNB AOTY Hackathon 2026 | Project: Ipfi Nyamande")
    print("=" * 65)
    print("Starting Django server at http://127.0.0.1:8000 ...")
    print("For mobile testing on same Wi-Fi: http://0.0.0.0:8000")
    print("Press Ctrl+C to stop the server.\n")

    cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nPfunzoBridge server stopped.")

if __name__ == '__main__':
    main()
