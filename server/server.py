import asyncio
import os
import sys
import logging

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

import json
import time
import subprocess
import urllib.request
import time
import ctypes
import zipfile
import threading
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import pyvirtualcam
import sounddevice as sd
import numpy as np
import cv2
import av
import customtkinter as ctk
import qrcode

def check_single_instance():
    mutex_name = "MobileCamera_USB_Streamer_Mutex_v1"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == 183: # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(0, "Mobile Camera is already running!\n\nPlease close the other instance before starting a new one.", "Mobile Camera Error", 0x10)
        sys.exit(0)
    return mutex

_app_mutex = check_single_instance()

app = FastAPI()

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller puts them in the root of _MEIPASS (because of --add-data "web\index.html;.")
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
        else:
            # cx_Freeze puts them in a "web" subdirectory (because of ("web", "web") in setup.py)
            base_path = os.path.dirname(sys.executable)
            if relative_path in ["index.html", "audio-processor.js"]:
                return os.path.join(base_path, "web", relative_path)
            return os.path.join(base_path, relative_path)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    # if it's web content, resolve to the sibling 'web' directory
    if relative_path in ["index.html", "audio-processor.js"]:
        return os.path.join(base_path, "..", "web", relative_path)
    return os.path.join(base_path, relative_path)

@app.get("/")
async def get():
    html_path = get_resource_path("index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

@app.get("/audio-processor.js")
async def get_audio_processor():
    html_path = get_resource_path("audio-processor.js")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content, media_type="application/javascript")

camera_rotation = 0

class LatestFrameSlot:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
    def put(self, frame):
        with self.lock:
            self.frame = frame
    def get(self):
        with self.lock:
            return self.frame

class AudioJitterBuffer:
    def __init__(self, max_ms=150, sample_rate=48000, channels=1, bytes_per_sample=2):
        self.lock = threading.Lock()
        self.buffer = bytearray()
        self.max_bytes = int((max_ms / 1000.0) * sample_rate * channels * bytes_per_sample)
    
    def push(self, data: bytes):
        with self.lock:
            self.buffer.extend(data)
            # Bound and drop oldest
            if len(self.buffer) > self.max_bytes:
                drop_len = len(self.buffer) - self.max_bytes
                # Ensure we drop in multiples of 2 bytes (16-bit)
                drop_len = (drop_len // 2) * 2
                self.buffer = self.buffer[drop_len:]
                
    def pull(self, n_bytes: int) -> bytes:
        with self.lock:
            if len(self.buffer) >= n_bytes:
                chunk = bytes(self.buffer[:n_bytes])
                self.buffer = self.buffer[n_bytes:]
                return chunk
            else:
                chunk = bytes(self.buffer)
                self.buffer.clear()
                # Pad with silence
                chunk += b'\x00' * (n_bytes - len(chunk))
                return chunk

latest_frame_slot = LatestFrameSlot()
audio_buffer = AudioJitterBuffer()

def process_video(img):
    global camera_rotation
    
    # 1. Apply the user's manual button rotation FIRST
    if camera_rotation == 90:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif camera_rotation == 180:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif camera_rotation == 270:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
    h, w, _ = img.shape
    
    # 2. Prevent stretching in apps like Google Meet by always outputting a Landscape frame.
    # If the image is Portrait (taller than it is wide), we must scale it to fit a landscape canvas.
    if h > w:
        # Target landscape dimensions (swap width and height)
        canvas_w = h
        canvas_h = w
        
        # Scale the image down so its height fits inside canvas_h
        scale = canvas_h / h
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        img_resized = cv2.resize(img, (new_w, new_h))
        
        # Create a solid black canvas (BGR)
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        
        # Calculate offsets to center the portrait image
        x_offset = (canvas_w - new_w) // 2
        y_offset = (canvas_h - new_h) // 2
        
        # Paste the portrait image into the center of the black canvas
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
        img = canvas
        
    return img

def virtualcam_worker():
    cam = None
    cam_format = None
    try:
        # Default initialization, wait for first frame
        while True:
            frame_img = latest_frame_slot.get()
            if frame_img is not None:
                img_processed = process_video(frame_img)
                h, w, _ = img_processed.shape
                
                if cam is None or cam.width != w or cam.height != h:
                    if cam: cam.close()
                    try:
                        # Try Unity Capture (Requires RGBA)
                        cam = pyvirtualcam.Camera(width=w, height=h, fps=30, fmt=pyvirtualcam.PixelFormat.RGBA, backend="unitycapture")
                        cam_format = "RGBA"
                    except Exception:
                        try:
                            # Fallback to OBS (Requires RGB)
                            cam = pyvirtualcam.Camera(width=w, height=h, fps=30, fmt=pyvirtualcam.PixelFormat.RGB, backend="obs")
                            cam_format = "RGB"
                        except Exception:
                            # Final generic fallback
                            cam = pyvirtualcam.Camera(width=w, height=h, fps=30, fmt=pyvirtualcam.PixelFormat.RGB)
                            cam_format = "RGB"
                
                # Convert the OpenCV frame based on the active driver's requirement
                if cam_format == "RGBA":
                    out_frame = cv2.cvtColor(img_processed, cv2.COLOR_BGR2RGBA)
                else:
                    out_frame = cv2.cvtColor(img_processed, cv2.COLOR_BGR2RGB)
                    
                cam.send(out_frame)
                cam.sleep_until_next_frame()
            else:
                time.sleep(0.01)
    except Exception as e:
        import traceback, os
        log_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'MobileCamera')
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'crash_log.txt'), 'w') as f:
            f.write("virtualcam_worker crashed:\n")
            f.write(traceback.format_exc())

def audio_worker():
    def callback(outdata, frames, time, status):
        bytes_needed = frames * 2 # 16-bit mono
        chunk = audio_buffer.pull(bytes_needed)
        # outdata expects shape (frames, channels)
        arr = np.frombuffer(chunk, dtype=np.int16).reshape(frames, 1)
        outdata[:] = arr
        
    try:
        # Attempt to find VB-Audio Virtual Cable Input automatically if present, otherwise default
        device_index = None
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if "CABLE Input" in dev['name']:
                device_index = i
                break
                
        with sd.OutputStream(device=device_index, samplerate=48000, channels=1, dtype='int16', callback=callback):
            while True:
                sd.sleep(1000)
    except Exception as e:
        print("Audio worker error:", e)

threading.Thread(target=virtualcam_worker, daemon=True).start()
threading.Thread(target=audio_worker, daemon=True).start()

@app.websocket("/ws/controls")
async def websocket_controls(websocket: WebSocket):
    await websocket.accept()
    global camera_rotation
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            cmd = parsed.get("command")
            val = parsed.get("value")
            if cmd == "rotation": 
                camera_rotation = int(val)
    except Exception:
        pass

@app.websocket("/ws/data")
async def ws_data(websocket: WebSocket):
    await websocket.accept()
    # Decoder per connection
    ctx = av.CodecContext.create("h264", "r")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                break
                
            tag = data[0]
            payload = data[1:]
            
            if tag == 0x01: # Video
                try:
                    for packet in ctx.parse(payload):
                        for frame in ctx.decode(packet):
                            bgr = frame.to_ndarray(format="bgr24")
                            latest_frame_slot.put(bgr)
                except av.error.FFmpegError:
                    pass
                except Exception:
                    pass
            elif tag == 0x02: # Audio
                audio_buffer.push(payload)
                
    except Exception:
        pass

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def setup_and_run_adb():
    adb_path = "adb"
    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.run([adb_path, "version"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
    except FileNotFoundError:
        import platform
        app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'MobileCamera')
        os.makedirs(app_data, exist_ok=True)
        local_adb_dir = os.path.join(app_data, "platform-tools")
        adb_path = os.path.join(local_adb_dir, "adb.exe" if os.name == 'nt' else "adb")
        
        if not os.path.exists(adb_path):
            try:
                url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
                zip_path = os.path.join(app_data, "platform-tools.zip")
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(app_data)
                os.remove(zip_path)
            except Exception as e:
                print("Failed to download ADB:", e)
                return
                
    while True:
        try:
            subprocess.run([adb_path, "reverse", "tcp:8000", "tcp:8000"], stdin=subprocess.DEVNULL, capture_output=True, creationflags=CREATE_NO_WINDOW)
        except Exception as e:
            pass
        time.sleep(3)

def run_gui():
    threading.Thread(target=setup_and_run_adb, daemon=True).start()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Mobile Camera (USB)")
    root.geometry("400x380")
    
    url = "http://127.0.0.1:8000"
    
    ctk.CTkLabel(root, text="Mobile Camera Server", font=("Arial", 20, "bold")).pack(pady=10)
    ctk.CTkLabel(root, text="Connect via USB Debugging", font=("Arial", 12)).pack(pady=5)
    
    qr = qrcode.make(url)
    qr = qr.resize((200, 200))
    qr_img = ctk.CTkImage(light_image=qr, dark_image=qr, size=(200, 200))
    lbl_qr = ctk.CTkLabel(root, image=qr_img, text="")
    lbl_qr.pack(pady=10)
    
    lbl_url = ctk.CTkLabel(root, text=url, font=("Arial", 14, "bold"))
    lbl_url.pack(pady=10)
    
    root.mainloop()

if __name__ == '__main__':
    threading.Thread(target=start_fastapi, daemon=True).start()
    run_gui()
