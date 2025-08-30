import os
import tempfile
import wave
import speech_recognition as sr
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox, QFileDialog
)

# --- Core + Hotword ---
from lyra_core import LyraCore
from modules.hotword import HotwordThread   # ✅ new


# -------------------- Recorder Thread --------------------
# -------------------- Recorder Thread --------------------
class RecorderThread(QThread):
    """Continuous mic recorder using SpeechRecognition + Whisper-friendly WAV"""
    recorded = pyqtSignal(str)  # emits path to WAV file

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def run(self):
        self._running = True
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("🎤 Listening… Speak something (Stop button to exit)")
            while self._running:
                try:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)

                    wav_path = tempfile.mkstemp(suffix=".wav")[1]
                    with open(wav_path, "wb") as f:
                        f.write(audio.get_wav_data(convert_rate=16000, convert_width=2))  # 16kHz PCM16

                    # Check silence before emitting
                    if not self.is_silent(wav_path):
                        self.recorded.emit(wav_path)
                    else:
                        print("⚠️ Silence detected, waiting for speech...")

                    # remove temp file
                    try:
                        os.remove(wav_path)
                    except:
                        pass

                except Exception as e:
                    print(f"⚠️ Recorder error: {e}")
                    continue

    def stop(self):
        self._running = False

    @staticmethod
    def is_silent(wav_path: str, threshold: int = 500) -> bool:
        """Check if audio RMS is below threshold"""
        import wave, audioop
        try:
            with wave.open(wav_path, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                rms = audioop.rms(frames, wf.getsampwidth())
                return rms < threshold
        except Exception:
            return False



# -------------------- Main UI --------------------
class LyraUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LYRA — Multilingual Voice Assistant")
        self.setMinimumSize(880, 620)

        self.core = LyraCore()

        # ===== Top controls =====
        self.lang_label = QLabel("TTS Language:")
        self.lang_select = QComboBox()
        self.lang_select.addItems(["auto", "en", "hi", "kn", "ta", "te", "mr", "bn"])
        self.lang_select.setCurrentText("auto")

        self.record_btn = QPushButton("● Start Recording")
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)

        self.upload_btn = QPushButton("Upload Audio…")
        self.upload_btn.clicked.connect(self.upload_audio)

        top_row = QHBoxLayout()
        top_row.addWidget(self.lang_label)
        top_row.addWidget(self.lang_select, 1)
        top_row.addStretch()
        top_row.addWidget(self.upload_btn)
        top_row.addWidget(self.record_btn)

        # ===== Middle: transcript & reply =====
        self.input_label = QLabel("You said:")
        self.input_box = QTextEdit()
        self.input_box.setReadOnly(True)

        self.output_label = QLabel("LYRA:")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # ===== Bottom: quick commands =====
        self.cmd_line = QLineEdit()
        self.cmd_line.setPlaceholderText("Type a command (e.g., 'open notepad', 'search weather')")
        self.cmd_line.returnPressed.connect(self.run_text_command)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_text_command)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.cmd_line, 1)
        bottom_row.addWidget(self.run_btn)

        # Layout
        root = QVBoxLayout()
        root.addLayout(top_row)
        root.addWidget(self.input_label)
        root.addWidget(self.input_box, 2)
        root.addWidget(self.output_label)
        root.addWidget(self.output_box, 2)
        root.addLayout(bottom_row)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.rec_thread = None

        # ===== Start hotword detection =====
        self.hotword_thread = HotwordThread()  # choose: "jarvis", "lyra", etc.
        self.hotword_thread.hotword_detected.connect(self.on_hotword)
        self.hotword_thread.start()

        # Greet
        self.append_reply("👋 Namaste! Hola! Hello! I’m LYRA. Say 'Lyra' or press Record to begin.")

    # ------------- Helpers -------------
    def append_me(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.input_box.append(f"[{ts}] You: {text}")

    def append_reply(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.output_box.append(f"[{ts}] LYRA: {text}")

    # ------------- Hotword Trigger -------------
    def on_hotword(self):
        """Triggered when hotword is detected."""
        self.append_reply("👂 Hotword detected! Listening for your command...")
        if not (self.rec_thread and self.rec_thread.isRunning()):
            self.record_btn.setChecked(True)
            self.toggle_recording(True)

    # ------------- Actions -------------
    def toggle_recording(self, checked):
        if checked:
            self.record_btn.setText("■ Stop Recording")
            self.rec_thread = RecorderThread()
            self.rec_thread.recorded.connect(self.on_recorded)
            self.rec_thread.start()
        else:
            self.record_btn.setText("● Start Recording")
            if self.rec_thread:
                self.rec_thread.stop()
                self.rec_thread.wait()

    def on_recorded(self, wav_path: str):
        out = self.core.process_audio(wav_path, preferred_tts_lang=self.lang_select.currentText())
        self.append_me(out["user_text"])
        self.append_reply(out["reply"])
        try:
            os.remove(wav_path)
        except Exception:
            pass

    def upload_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select an audio file", "", "Audio Files (*.wav *.mp3 *.m4a)")
        if path:
            out = self.core.process_audio(path, preferred_tts_lang=self.lang_select.currentText())
            self.append_me(out["user_text"])
            self.append_reply(out["reply"])

    def run_text_command(self):
        text = self.cmd_line.text().strip()
        if not text:
            return
        self.append_me(text)
        out = self.core.process_text(text, preferred_tts_lang=self.lang_select.currentText())
        self.append_reply(out["reply"])
        self.cmd_line.clear()