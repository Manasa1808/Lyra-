import os
import tempfile
import wave
import audioop
from datetime import datetime

# ---------- FFmpeg Path Setup ----------
ffmpeg_path = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"
os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

# ---------- STT / TTS ----------
import whisper
from gtts import gTTS
import pyttsx3
from langdetect import detect as lang_detect
import pygame

# ---------- Tasks ----------
from modules.apps import open_app, close_app
from modules.websearch import search_and_summarise
from modules.weather import get_weather, get_time_str
from modules.emotions import SentimentModel
from modules.system import (
    take_screenshot, lock_pc, shutdown_pc, restart_pc,
    increase_volume, decrease_volume,
    increase_brightness, decrease_brightness
)


def safe_lang_detect(text: str) -> str:
    try:
        return lang_detect(text)
    except Exception:
        return "en"


class LyraCore:
    def __init__(self):
        self.asr = whisper.load_model("base")
        self.tts_engine = pyttsx3.init()
        self.sentiment = SentimentModel()

        pygame.mixer.init()
        self.history = []

        # ---------- Multilingual keyword maps ----------
        self.greeting_words = [
            "hello", "hi", "hey", "hola", "namaste", "नमस्ते", "ಹಲೋ", "வணக்கம்", "నమస్తే", "bonjour", "ciao"
        ]
        self.open_words = ["open", "launch", "start", "खोलो", "खोलना", "iniciar", "abrir", "ouvrir", "avvia"]
        self.close_words = ["close", "quit", "exit", "kill", "बंद", "salir", "cerrar", "fermer", "uscire"]
        self.search_words = ["search", "look up", "google", "web search", "buscar", "recherche", "தேடுங்கள்"]
        self.weather_words = ["weather", "temperature", "clima", "मौसम", "climat", "ಹವಾಮಾನ", "కాలావస్థ"]
        self.time_words = ["time", "date", "day", "hora", "तारीख", "samay", "temps", "tempo"]
        self.screenshot_words = ["screenshot", "take a screenshot", "capture screen"]
        self.volume_up_words = ["increase volume", "volume up", "raise volume"]
        self.volume_down_words = ["decrease volume", "volume down", "lower volume"]
        self.brightness_up_words = ["increase brightness", "brighter", "brightness up"]
        self.brightness_down_words = ["decrease brightness", "dim", "brightness down"]
        self.lock_words = ["lock pc", "lock computer"]
        self.shutdown_words = ["shutdown", "turn off pc"]
        self.restart_words = ["restart", "reboot"]

        self.emotion_words = {
            "NEGATIVE": ["sad", "angry", "stressed", "lonely", "upset", "help", 
                         "दुखी", "गुस्सा", "तनाव", "एकाकी", "उदास", "मदद",
                         "triste", "enojado", "estresado", "solo", "déprimé"],
            "POSITIVE": ["happy", "excited", "great", "good", "awesome", 
                         "खुश", "उत्साहित", "अच्छा", "शानदार",
                         "feliz", "contento", "super", "formidable"]
        }

    # ---------- Silence Detection ----------
    def is_silent(self, wav_path: str, threshold: int = 500) -> bool:
        """Check if audio RMS is below threshold"""
        try:
            with wave.open(wav_path, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                rms = audioop.rms(frames, wf.getsampwidth())
                return rms < threshold
        except Exception:
            return False

    # ---------- STT ----------
    def transcribe(self, audio_path: str) -> dict:
        result = self.asr.transcribe(audio_path)
        text = (result.get("text") or "").strip()
        lang = result.get("language") or safe_lang_detect(text)
        return {"text": text, "language": lang}

    # ---------- TTS ----------
    def tts_to_file(self, text: str, lang_code: str = "en") -> str:
        try:
            mp3_path = os.path.join(tempfile.gettempdir(), "lyra_tts.mp3")
            gTTS(text=text, lang=lang_code).save(mp3_path)
            self._play_file(mp3_path)
            return mp3_path
        except Exception:
            wav_path = os.path.join(tempfile.gettempdir(), "lyra_tts.wav")
            self.tts_engine.save_to_file(text, wav_path)
            self.tts_engine.runAndWait()
            self._play_file(wav_path)
            return wav_path

    def _play_file(self, path: str):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Audio playback failed: {e}")

    # ---------- Intents ----------
    def detect_intent(self, text: str) -> str:
        t = text.lower()
        if any(g in t for g in self.greeting_words):
            return "GREETING"
        if any(word in t for word in self.open_words):
            return "OPEN_APP"
        if any(word in t for word in self.close_words):
            return "CLOSE_APP"
        if any(word in t for word in self.search_words):
            return "WEB_SEARCH"
        if any(word in t for word in self.weather_words):
            return "WEATHER"
        if any(word in t for word in self.time_words):
            return "TIME"
        if any(word in t for word in self.screenshot_words):
            return "SCREENSHOT"
        if any(word in t for word in self.volume_up_words):
            return "VOLUME_UP"
        if any(word in t for word in self.volume_down_words):
            return "VOLUME_DOWN"
        if any(word in t for word in self.brightness_up_words):
            return "BRIGHTNESS_UP"
        if any(word in t for word in self.brightness_down_words):
            return "BRIGHTNESS_DOWN"
        if any(word in t for word in self.lock_words):
            return "LOCK_PC"
        if any(word in t for word in self.shutdown_words):
            return "SHUTDOWN_PC"
        if any(word in t for word in self.restart_words):
            return "RESTART_PC"
        if any(word in t for word in self.emotion_words["NEGATIVE"]):
            return "SUPPORT"
        if "repeat" in t or "what did i say" in t or "previous" in t or "दोहराओ" in t or "repite" in t:
            return "CONTEXT"
        return "GENERAL"

    # ---------- Orchestrators ----------
    def process_audio(self, audio_path: str, preferred_tts_lang: str = "auto") -> dict:
        if self.is_silent(audio_path):
            return {"user_text": "", "reply": "", "intent": "SILENCE", "sentiment": "NEUTRAL", "lang": "en"}
        stt = self.transcribe(audio_path)
        if len(stt["text"].strip()) < 2:
            return {"user_text": "", "reply": "", "intent": "SILENCE", "sentiment": "NEUTRAL", "lang": stt["language"]}
        return self._respond(stt["text"], user_lang=stt["language"], preferred_tts_lang=preferred_tts_lang)

    def process_text(self, text: str, preferred_tts_lang: str = "auto") -> dict:
        if len(text.strip()) < 2:
            return {"user_text": "", "reply": "", "intent": "SILENCE", "sentiment": "NEUTRAL", "lang": safe_lang_detect(text)}
        user_lang = safe_lang_detect(text)
        return self._respond(text, user_lang=user_lang, preferred_tts_lang=preferred_tts_lang)

    # ---------- Core Response ----------
    def _respond(self, user_text: str, user_lang: str, preferred_tts_lang: str = "auto") -> dict:
        trimmed_text = user_text.strip()
        intent = self.detect_intent(trimmed_text)
        sentiment = self.sentiment.classify(trimmed_text)
        reply = ""

        tts_lang = preferred_tts_lang if preferred_tts_lang != "auto" else (user_lang or "en")

        if intent == "GREETING":
            reply = self._greeting_reply(sentiment, user_lang)
        elif intent == "OPEN_APP":
            reply = open_app(trimmed_text)
        elif intent == "CLOSE_APP":
            reply = close_app(trimmed_text)
        elif intent == "WEB_SEARCH":
            reply = search_and_summarise(trimmed_text)
        elif intent == "WEATHER":
            city = self._extract_city(trimmed_text)
            reply = get_weather(city) if city else "Please say the city, e.g., 'weather Bangalore'."
        elif intent == "TIME":
            reply = get_time_str()
        elif intent == "SUPPORT":
            reply = self._support_reply(sentiment)
        elif intent == "CONTEXT":
            reply = self._context_reply()
        else:
            reply = f"You said: {trimmed_text}"
        if intent == "SCREENSHOT":
            path = take_screenshot()
            reply = f"Screenshot saved as {path}"
        elif intent == "VOLUME_UP":
            increase_volume()
            reply = "Volume increased!"
        elif intent == "VOLUME_DOWN":
            decrease_volume()
            reply = "Volume decreased!"
        elif intent == "BRIGHTNESS_UP":
            increase_brightness()
            reply = "Brightness increased!"
        elif intent == "BRIGHTNESS_DOWN":
            decrease_brightness()
            reply = "Brightness decreased!"
        elif intent == "LOCK_PC":
            lock_pc()
            reply = "PC locked!"
        elif intent == "SHUTDOWN_PC":
            shutdown_pc()
            reply = "Shutting down..."
        elif intent == "RESTART_PC":
            restart_pc()
            reply = "Restarting..."
        elif sentiment == "NEGATIVE":
            reply = "I’m here with you. " + reply
        elif sentiment == "POSITIVE":
            reply = "Love the energy! " + reply
        else:
            reply = f"You said: {trimmed_text}"

        # Skip silent responses in history
        if intent != "SILENCE":
            self.history.append({"user": trimmed_text, "bot": reply, "ts": datetime.now().isoformat()})
            self.history = self.history[-5:]

        if reply:
            self.tts_to_file(reply, lang_code=tts_lang)

        return {"user_text": trimmed_text, "reply": reply, "intent": intent, "sentiment": sentiment, "lang": user_lang}

    # ---------- Helpers ----------
    def _extract_city(self, text: str) -> str | None:
        t = text.strip()
        if any(w in t.lower() for w in self.weather_words):
            parts = t.split()
            try:
                idx = [i for i, w in enumerate(parts) if w.lower() in ("weather", "in", "मौसम", "clima")][-1]
                if idx + 1 < len(parts):
                    return parts[idx + 1].strip(",. ")
            except Exception:
                pass
        return None

    def _greeting_reply(self, sentiment: str, lang: str) -> str:
        base = {
            "en": "Hello! How can I help you today?",
            "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकती हूँ?",
            "kn": "ನಮಸ್ಕಾರ! ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "ta": "வணக்கம்! நான் எப்படி உதவலாம்?",
            "te": "నమస్తే! నేను ఎలా సహాయం చేయగలను?",
            "bn": "নমস্কার! আমি কীভাবে সাহায্য করতে পারি?",
            "mr": "नमस्कार! मी कशी मदत करू शकते?",
            "es": "¡Hola! ¿Cómo puedo ayudarte?",
            "fr": "Bonjour ! Comment puis-je vous aider?",
            "it": "Ciao! Come posso aiutarti?"
        }
        msg = base.get(lang, base["en"])
        if sentiment == "POSITIVE":
            msg = "Great to hear from you! " + msg
        return msg

    def _support_reply(self, sentiment: str) -> str:
        if sentiment == "NEGATIVE":
            return "Take a slow breath. Would you like me to play calming music or note what’s bothering you?"
        if sentiment == "NEUTRAL":
            return "I’m here. Tell me what’s on your mind, and we’ll take it one step at a time."
        return "You sound upbeat! Want to channel that into a quick plan for your day?"

    def _context_reply(self) -> str:
        if not self.history:
            return "I don’t have prior context yet."
        last = self.history[-1]["user"]
        return f"You previously said: {last}" if len(last) > 2 else ""