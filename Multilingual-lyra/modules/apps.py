# modules/apps.py
import os
import subprocess
import webbrowser
import platform
import psutil
import pyautogui
import datetime

# -------- Multilingual keyword mapping --------
command_map = {
    "notepad": ["notepad", "editor", "पैड", "bloc de notas", "bloc-notes", "ಬ್ಲಾಕ್ ನೋಟ್ಸ್"],
    "calculator": ["calculator", "calc", "गणना", "calculadora", "calculatrice", "ಕ್ಯಾಲ್ಕುಲೇಟರ್"],
    "browser": ["chrome", "browser", "ब्राउज़र", "navegador", "navigateur", "ಬ್ರೌಸರ್"],
    "explorer": ["explorer", "files", "फाइल", "explorador", "explorateur"],
    "paint": ["paint", "drawing", "पेंट", "pintar", "peindre", "ಚಿತ್ರಕಲೆ"],
    "word": ["word", "ms word", "document", "शब्द", "documento", "document"],
    "excel": ["excel", "spreadsheet", "एक्सेल", "hoja", "tableur"],
    "powerpoint": ["powerpoint", "presentation", "प्रस्तुति", "presentación", "présentation"],
    "cmd": ["cmd", "command prompt", "terminal", "कमांड", "consola", "invite"],
    "screenshot": ["screenshot", "capture", "स्क्रीनशॉट", "captura", "capture écran"],
    "shutdown": ["shutdown", "power off", "बंद", "apagar", "arrêter"],
    "restart": ["restart", "reboot", "रीस्टार्ट", "reiniciar", "redémarrer"]
}


def open_app(command: str) -> str:
    cmd_lower = command.lower()

    # --- Browser ---
    if any(word in cmd_lower for word in command_map["browser"]):
        webbrowser.open("https://www.google.com")
        return "Opening browser."

    # --- Notepad ---
    if any(word in cmd_lower for word in command_map["notepad"]):
        os.system("notepad")
        return "Opening Notepad."

    # --- Calculator ---
    if any(word in cmd_lower for word in command_map["calculator"]):
        os.system("calc")
        return "Opening Calculator."

    # --- File Explorer ---
    if any(word in cmd_lower for word in command_map["explorer"]):
        os.system("explorer")
        return "Opening File Explorer."

    # --- Paint ---
    if any(word in cmd_lower for word in command_map["paint"]):
        os.system("mspaint")
        return "Opening Paint."

    # --- MS Word ---
    if any(word in cmd_lower for word in command_map["word"]):
        subprocess.Popen([r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"])
        return "Opening Word."

    # --- Excel ---
    if any(word in cmd_lower for word in command_map["excel"]):
        subprocess.Popen([r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"])
        return "Opening Excel."

    # --- PowerPoint ---
    if any(word in cmd_lower for word in command_map["powerpoint"]):
        subprocess.Popen([r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"])
        return "Opening PowerPoint."

    # --- CMD ---
    if any(word in cmd_lower for word in command_map["cmd"]):
        os.system("start cmd")
        return "Opening Command Prompt."

    # --- Screenshot ---
    if any(word in cmd_lower for word in command_map["screenshot"]):
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        return f"Screenshot saved as {filename}."

    # --- Shutdown ---
    if any(word in cmd_lower for word in command_map["shutdown"]):
        os.system("shutdown /s /t 1")
        return "Shutting down system."

    # --- Restart ---
    if any(word in cmd_lower for word in command_map["restart"]):
        os.system("shutdown /r /t 1")
        return "Restarting system."

    return "I couldn't recognize the application to open."


def close_app(command: str) -> str:
    cmd_lower = command.lower()

    if any(word in cmd_lower for word in command_map["notepad"]):
        os.system("taskkill /f /im notepad.exe")
        return "Closed Notepad."

    if any(word in cmd_lower for word in command_map["calculator"]):
        os.system("taskkill /f /im Calculator.exe")
        return "Closed Calculator."

    if any(word in cmd_lower for word in command_map["paint"]):
        os.system("taskkill /f /im mspaint.exe")
        return "Closed Paint."

    if any(word in cmd_lower for word in command_map["word"]):
        os.system("taskkill /f /im WINWORD.EXE")
        return "Closed Word."

    if any(word in cmd_lower for word in command_map["excel"]):
        os.system("taskkill /f /im EXCEL.EXE")
        return "Closed Excel."

    if any(word in cmd_lower for word in command_map["powerpoint"]):
        os.system("taskkill /f /im POWERPNT.EXE")
        return "Closed PowerPoint."

    if any(word in cmd_lower for word in command_map["cmd"]):
        os.system("taskkill /f /im cmd.exe")
        return "Closed Command Prompt."

    return "I couldn't recognize the application to close."