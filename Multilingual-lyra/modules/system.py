import os
import pyautogui
from datetime import datetime

# ---------- Screenshot ----------
def take_screenshot(save_path=None):
    if save_path is None:
        save_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img = pyautogui.screenshot()
    img.save(save_path)
    return save_path

# ---------- Lock / Shutdown / Restart ----------
def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")

def shutdown_pc():
    os.system("shutdown /s /t 0")

def restart_pc():
    os.system("shutdown /r /t 0")

# ---------- Volume Control (requires nircmd.exe in PATH) ----------
def increase_volume(step=10):
    os.system(f"nircmd.exe changesysvolume {int(step*655.35)}")

def decrease_volume(step=10):
    os.system(f"nircmd.exe changesysvolume -{int(step*655.35)}")

# ---------- Brightness Control (PowerShell) ----------
def increase_brightness(step=10):
    os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{step})")

def decrease_brightness(step=10):
    os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,-{step})")