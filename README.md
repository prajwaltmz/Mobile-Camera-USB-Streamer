# Mobile Camera USB Streamer 🎥📱

Turn your iPhone or Android phone into a high-quality wireless webcam and microphone for your PC! 
This project streams video and audio directly from your phone's browser over your local Wi-Fi network and creates a Virtual Camera and Virtual Microphone on your PC that can be used in Google Meet, Zoom, Discord, and Teams.

## ✨ Features
- **Zero App Install:** Runs entirely in your phone's web browser (Safari/Chrome). No need to download any apps from the App Store or Google Play!
- **USB Tethering (Zero Lag):** Uses ADB reverse port forwarding to stream directly over a USB cable. Extremely low latency and no Wi-Fi network required!
- **Sleek Desktop GUI:** Easy-to-use desktop application with a scannable QR code.
- **Smart Portrait Mode (Pillarboxing):** Prevents Google Meet from stretching your vertical video! Automatically pads portrait video with black bars to fit standard 16:9 meeting dimensions flawlessly.
- **Dual Streaming:** Streams both high-quality Video and Audio simultaneously.
- **Bulletproof Driver Compatibility:** Automatically scans your PC and connects flawlessly to either Unity Video Capture or OBS Virtual Camera, depending on what you have installed.
- **Single-Instance Protection:** Prevents driver locks and crashing by ensuring only one camera instance runs at a time.

---

## 🛠️ Installation

### 1. Python Environment Setup (For Developers)
*Note: You can skip this if you are using the compiled `.exe` or `.msi` application.*
1. Double-click **`install.bat`**.
2. This will automatically create a virtual environment (`venv`) and install all required Python packages.

### 2. Install the Virtual Drivers
To route your video and audio into Google Meet, you need to install the virtual drivers.
1. **Video Driver (Choose ONE):** 
   - Option A (Recommended): Run **`install_driver_unity.bat`** as Administrator (Installs Unity Video Capture - highly stable).
   - Option B: Run **`install_driver_obs.bat`** (Installs OBS Studio - good if you already use OBS).
2. **Audio Driver:** Run **`install_driver_vbaudio.bat`** (Installs VB-Cable, which provides the virtual microphone).

---

## 🚀 How to Use

### Step 1: Connect Your Phone via USB
1. Plug your Android phone or iPhone into your PC using a high-quality USB cable.
2. Ensure **USB Debugging** is enabled on your phone (required for the incredibly fast USB tethering).

### Step 2: Start the App
1. Run the **MobileCamera** application (or `run.bat` if running from source).
2. A beautiful desktop window will open displaying a QR code.

### Step 3: Connect your Phone's Browser
1. Scan the QR code on the desktop app using your phone's camera, or simply open Chrome/Safari and type:
   `http://127.0.0.1:8000`
2. Since this streams securely over the USB cable directly to localhost, there are no "unsafe HTTPS" warnings!
3. When prompted, allow the browser permission to use your Camera and Microphone.
4. Tap the screen to start streaming!

### Step 3: Use it in Meetings (Google Meet / Zoom)
Open your meeting app on your PC and change your device settings:
- **Video / Camera:** Select **Unity Video Capture** (or **OBS Virtual Camera** if you installed Option B)
- **Audio / Microphone:** Select **CABLE Output (VB-Audio Virtual Cable)**

---

## 📦 Building for Distribution

You don't need to share the Python code if you want to send this to a friend. You can compile it into an easy-to-use application!

**Option A: Standalone Executable (Fastest)**
- Run **`build.bat`**.
- It will safely compress the entire app into one single portable file located at `dist\MobileCamera.exe`. You can send this one single `.exe` file to anyone, and they can run it instantly without installing Python.

**Option B: Full Windows Installer (.msi)**
- Run **`build_setup.bat`**.
- It will generate a professional `.msi` Windows setup file inside the `dist\` folder. Running this will install the app into the user's Start Menu exactly like a normal Windows program.

---

## 🗑️ Uninstallation & Troubleshooting

If you ever need to uninstall the virtual drivers from your PC:
- **Video:** Run `uninstall_driver_unity.bat` OR `uninstall_driver_obs.bat`
- **Audio:** Run `uninstall_driver_vbaudio.bat`

**Camera Unavailable Error in Meet?**
If you see a "Camera unavailable" error, it means the driver is locked by another instance of the app. 
1. Make sure you don't have multiple copies of Mobile Camera running in the background. 
2. If all else fails, simply restart your PC to clear any locked files.
