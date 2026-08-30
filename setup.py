import sys
from cx_Freeze import setup, Executable
import os
import pyvirtualcam

# Get the paths
pyvirtualcam_dir = os.path.dirname(pyvirtualcam.__file__)
site_packages_dir = os.path.dirname(pyvirtualcam_dir)
av_libs_dir = os.path.join(site_packages_dir, "av.libs")

# Include the web directory, certs, and native binaries
include_files = [
    ("web", "web"),
    ("server/cert.pem", "server/cert.pem"),
    ("server/key.pem", "server/key.pem"),
]

if os.path.exists(av_libs_dir):
    include_files.append((av_libs_dir, "lib/av.libs"))

# Add pyvirtualcam native backends safely
for file in os.listdir(pyvirtualcam_dir):
    if file.endswith(".pyd"):
        src = os.path.join(pyvirtualcam_dir, file)
        dst = f"lib/pyvirtualcam/{file}"
        include_files.append((src, dst))

build_exe_options = {
    "packages": ["fastapi", "uvicorn", "pyvirtualcam", "cv2", "numpy", "av", "aiortc"],
    "zip_include_packages": [],
    "include_files": include_files,
    "excludes": [],
    "include_msvcr": True,
}

base = "gui" if sys.platform == "win32" else None

setup(
    name="MobileCamera",
    version="1.0",
    description="Use your phone as a high-quality PC webcam.",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "server/server.py", 
            base=base, 
            target_name="MobileCamera.exe",
            shortcut_name="Mobile Camera",
            shortcut_dir="ProgramMenuFolder",
            icon="icon.ico"
        )
    ]
)
