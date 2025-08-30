 # modules/hotword.py
import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal

class HotwordThread(QThread):
    hotword_detected = pyqtSignal()

    def __init__(self, hotword="lyra",parent=None):
        super().__init__()
        self.hotword = hotword.lower()
        self._running = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def run(self):
        self._running = True
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print(f"🎤 Hotword listening for '{self.hotword}'...")

            while self._running:
                try:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio, language="en-IN").lower()
                    print(f"Detected: {text}")
                    if self.hotword in text:
                        print("✅ Hotword detected!")
                        self.hotword_detected.emit()
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"⚠️ Hotword error: {e}")
                    continue

    def stop(self):
        self._running = False