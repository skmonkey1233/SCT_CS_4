import subprocess
import sys
import os

def build():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build the executable
    args = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "EducationalKeylogger",
        "test4.py"
    ]
    print("Running PyInstaller...")
    subprocess.run(args, check=True)
    print("Build finished. Find your executable in the 'dist' folder.")

if __name__ == "__main__":
    build()
