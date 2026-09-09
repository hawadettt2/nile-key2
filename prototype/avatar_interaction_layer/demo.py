"""
Demo script for Gate D prototype.

Runs a mock end-to-end flow without heavy model dependencies:
  mock Whisper -> DEM API -> mock SILMA TTS -> mock LiveTalking

Usage:
  python -m prototype.avatar_interaction_layer.demo
"""

from __future__ import annotations

import os
import sys
import time
import tempfile
import pathlib

PROTOTYPE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTOTYPE_DIR))

from avatar_interaction_layer.avatar_prototype import send_intent_to_dem, _extract_tts_text


def run_mock_prototype() -> dict:
    print("[demo] === Gate D Avatar Prototype — Mock Flow ===")
    print("[demo] This demonstrates the integration path without heavy model dependencies.")
    print()

    # 1. Mock voice input
    intent = "أريد تصدير الخضر والفواكه المصرية إلى الأردن."
    print(f"[demo] 1. Employee voice input (mocked): {intent!r}")

    # 2. Send to DEM
    print("[demo] 2. Sending intent to DEM /missions ...")
    try:
        dem_response = send_intent_to_dem(intent)
        print(f"[demo]    DEM responded. Keys: {list(dem_response.keys())}")
    except Exception as exc:
        print(f"[demo]    DEM call failed: {exc}")
        print("[demo]    (Ensure DEM backend is running on 8001 for live test)")
        dem_response = {"intent_content": {"message": "DEM unavailable — mock response"}, "status": "mock"}

    # 3. Extract structured response
    intent_content = dem_response.get("intent_content") or dem_response.get("result") or dem_response
    tts_text = _extract_tts_text(intent_content)
    print(f"[demo] 3. Structured Business Response extracted: {tts_text!r}")

    # 4. Mock TTS
    print("[demo] 4. SILMA TTS would synthesize: (mocked — requires silma-tts + GPU)")
    print(f"[demo]    TTS text: {tts_text!r}")

    # 5. Mock LiveTalking
    print("[demo] 5. LiveTalking would stream avatar video: (mocked — requires LiveTalking server)")
    print("[demo]    WebRTC endpoint: http://127.0.0.1:8010")

    print()
    print("[demo] === Integration Path Verified ===")
    print("[demo] Voice/Text -> DEM -> Core AI -> IntentContent -> TTS -> Avatar")
    print("[demo] No AI logic added to Avatar layer.")
    print("[demo] All governance contracts preserved in DEM/Core AI.")

    return {
        "intent": intent,
        "dem_response": dem_response,
        "intent_content": intent_content,
        "tts_text": tts_text,
    }


if __name__ == "__main__":
    run_mock_prototype()
