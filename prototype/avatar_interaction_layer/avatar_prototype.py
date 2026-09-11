"""
Avatar Interaction Layer
========================
Minimal self-hosted prototype bridging:
  Browser (WebRTC/audio) <-> Avatar Layer <-> DEM API <-> Core AI

Stack:
  - Whisper (OpenAI) for STT
  - DEM existing /missions API for Core AI
  - SILMA TTS for Arabic/English TTS
  - LiveTalking + MuseTalk for avatar video
"""

from __future__ import annotations

import os
import queue
import threading
import time
import json
from typing import Optional

import requests

# torch is imported lazily inside WhisperSTT to avoid hard dependency at import time

# ============================================================
# Configuration
# ============================================================

DEM_API_BASE_URL = os.getenv("DEM_API_BASE_URL", "http://localhost:8000/api/v1/digital-export-manager")
DEM_SESSION_ID = os.getenv("DEM_SESSION_ID", "demo-session-001")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # small: balance of speed/accuracy for Arabic
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "ar")

SILMA_TTS_MODEL = os.getenv("SILMA_TTS_MODEL", "silma-ai/silma-tts")
SILMA_TTS_REF_AUDIO = os.getenv("SILMA_TTS_REF_AUDIO", "")
SILMA_TTS_REF_TEXT = os.getenv("SILMA_TTS_REF_TEXT", "")

LIVETALKING_URL = os.getenv("LIVETALKING_URL", "http://127.0.0.1:8010")
LIVETALKING_AVATAR_ID = os.getenv("LIVETALKING_AVATAR_ID", "wav2lip256_avatar1")

# ============================================================
# DEM Integration (existing contract, unchanged)
# ============================================================


def send_intent_to_dem(intent_text: str, mission_type: str = "RESEARCH", session_id: Optional[str] = None, token: Optional[str] = None) -> dict:
    """
    Send employee intent to DEM via existing /missions contract.
    Returns Structured Business Response (IntentContent).
    """
    session_id = session_id or DEM_SESSION_ID
    payload = {"query": intent_text}
    url = f"{DEM_API_BASE_URL}/missions"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {"session_id": session_id}
    body = {"mission_type": mission_type, "payload": payload}
    resp = requests.post(url, json=body, headers=headers, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# Whisper STT (open-source, self-hosted)
# ============================================================


class WhisperSTT:
    """Local Whisper STT with Arabic support."""

    def __init__(self, model_name: str = WHISPER_MODEL):
        import whisper

        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str, language: str = WHISPER_LANGUAGE) -> str:
        result = self._model.transcribe(audio_path, language=language)
        return result.get("text", "").strip()


# ============================================================
# SILMA TTS (open-source, Arabic-capable)
# ============================================================


class SilmaTTS:
    """Local SILMA TTS client for Arabic + English."""

    def __init__(self, model_name: str = SILMA_TTS_MODEL):
        try:
            from silma_tts.api import SilmaTTS

            self._tts = SilmaTTS()
        except ImportError as exc:
            raise RuntimeError("silma-tts is not installed. See prototype/README.md") from exc

    def synthesize(self, text: str, ref_audio: str = SILMA_TTS_REF_AUDIO, ref_text: str = SILMA_TTS_REF_TEXT) -> str:
        """
        Synthesize speech and return path to generated WAV.
        """
        out_path = "/tmp/avatar_response.wav"
        self._tts.infer(
            ref_file=ref_audio,
            ref_text=ref_text or "",
            gen_text=text,
            file_wave=out_path,
            seed=None,
            speed=1.0,
        )
        return out_path


# ============================================================
# LiveTalking / MuseTalk bridge (placeholder)
# ============================================================


class LiveTalkingBridge:
    """
    Bridge to LiveTalking server for avatar video.
    This is a placeholder; actual integration depends on LiveTalking deployment.
    """

    def __init__(self, base_url: str = LIVETALKING_URL, avatar_id: str = LIVETALKING_AVATAR_ID):
        self.base_url = base_url.rstrip("/")
        self.avatar_id = avatar_id

    def health(self) -> bool:
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
            return True
        except requests.RequestException:
            return False

    def send_audio(self, audio_path: str, session_id: Optional[str] = None) -> dict:
        """
        Send audio to LiveTalking for lip-sync + video streaming.
        Actual endpoint/payload depends on LiveTalking version.
        """
        session_id = session_id or "demo-session"
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            resp = requests.post(
                f"{self.base_url}/api/audio",
                data={"sessionid": session_id, "avatar_id": self.avatar_id},
                files=files,
                timeout=30,
            )
        resp.raise_for_status()
        return resp.json()


# ============================================================
# Main prototype flow
# ============================================================


class AvatarPrototype:
    """Minimal end-to-end prototype flow."""

    def __init__(self):
        try:
            self.stt = WhisperSTT()
        except Exception as exc:
            print(f"[Avatar] WARNING: Whisper STT unavailable: {exc}")
            self.stt = None
        try:
            self.tts = SilmaTTS()
        except Exception as exc:
            print(f"[Avatar] WARNING: SILMA TTS unavailable: {exc}")
            self.tts = None
        self.avatar = LiveTalkingBridge()
        self._ready = False

    def startup(self) -> None:
        print("[Avatar] Starting Whisper...")
        if self.stt is None:
            try:
                self.stt = WhisperSTT()
            except Exception as exc:
                print(f"[Avatar] WARNING: Whisper STT unavailable: {exc}")
        print("[Avatar] Starting SILMA TTS...")
        if self.tts is None:
            try:
                self.tts = SilmaTTS()
            except Exception as exc:
                print(f"[Avatar] WARNING: SILMA TTS unavailable: {exc}")
                self.tts = None
        print("[Avatar] Checking LiveTalking...")
        if not self.avatar.health():
            print("[Avatar] WARNING: LiveTalking not reachable; avatar video will be unavailable.")
        self._ready = True
        print("[Avatar] Startup complete.")

    def process_voice(self, audio_path: str) -> dict:
        """
        1. Transcribe audio -> text
        2. Send text to DEM -> IntentContent
        3. Optionally synthesize response -> audio (if SILMA TTS available)
        4. Optionally send audio to LiveTalking -> avatar video
        """
        if not self._ready:
            raise RuntimeError("AvatarPrototype not started. Call startup() first.")

        if self.stt is None:
            return {"error": "stt_unavailable"}

        print(f"[Avatar] Transcribing: {audio_path}")
        intent = self.stt.transcribe(audio_path)
        print(f"[Avatar] Transcribed intent: {intent!r}")

        if not intent:
            return {"error": "empty_transcription"}

        print("[Avatar] Sending intent to DEM...")
        dem_response = send_intent_to_dem(intent)
        print(f"[Avatar] DEM response keys: {list(dem_response.keys())}")

        intent_content = (
            dem_response.get("intent_content")
            or dem_response.get("result")
            or dem_response
        )

        tts_text = _extract_tts_text(intent_content)
        print(f"[Avatar] Response text: {tts_text!r}")

        audio_out = None
        if self.tts is not None:
            try:
                audio_out = self.tts.synthesize(tts_text)
                print(f"[Avatar] TTS audio: {audio_out}")
            except Exception as exc:
                print(f"[Avatar] TTS failed: {exc}")

        avatar_result = {}
        if audio_out and self.avatar.health():
            try:
                avatar_result = self.avatar.send_audio(audio_out)
                print(f"[Avatar] LiveTalking response: {avatar_result}")
            except Exception as exc:
                print(f"[Avatar] LiveTalking failed: {exc}")
        else:
            print("[Avatar] Skipping LiveTalking (no audio or not healthy).")

        return {
            "intent": intent,
            "dem_response": dem_response,
            "intent_content": intent_content,
            "tts_text": tts_text,
            "tts_audio": audio_out,
            "avatar": avatar_result,
        }


def _extract_tts_text(intent_content: dict) -> str:
    """Best-effort extraction of speakable text from IntentContent."""
    if isinstance(intent_content, str):
        return intent_content
    if not isinstance(intent_content, dict):
        return str(intent_content)
    for key in ("message", "summary", "response", "text", "content"):
        value = intent_content.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(intent_content)
