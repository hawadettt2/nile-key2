"""
Avatar Interaction Layer Server
================================
Minimal FastAPI server exposing:
  - GET  /            -> web client
  - WS   /ws/avatar   -> WebSocket for audio/transcript/webrtc
  - POST /api/process_audio -> optional HTTP audio upload fallback

Run:
  python -m prototype.avatar-interaction-layer.server
"""

from __future__ import annotations

import os
import json
import base64
import pathlib
import tempfile
import threading
import queue
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure prototype package is importable when run as script
PROTOTYPE_DIR = pathlib.Path(__file__).resolve().parent.parent
import sys

sys.path.append(str(PROTOTYPE_DIR))

from avatar_interaction_layer.avatar_prototype import AvatarPrototype, send_intent_to_dem, DEM_API_BASE_URL, DEM_SESSION_ID

app = FastAPI(title="Avatar Interaction Layer — Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static web client
WEB_CLIENT_DIR = PROTOTYPE_DIR / "web-client"
if WEB_CLIENT_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_CLIENT_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(WEB_CLIENT_DIR / "index.html"))


from pydantic import BaseModel
from fastapi import Body


class TextIntentRequest(BaseModel):
    text: str
    mission_type: str = "create_mission"
    session_id: Optional[str] = None
    token: Optional[str] = None


@app.post("/api/text-intent")
def text_intent_endpoint(body: TextIntentRequest):
    """
    HTTP fallback for text-only interaction with Core AI via DEM.
    Returns structured response for the Avatar UI.
    """
    text = (body.text or "").strip()
    if not text:
        return {"error": "empty_text"}
    try:
        session_id = body.session_id or DEM_SESSION_ID
        payload = {"query": text}
        url = f"{DEM_API_BASE_URL}/missions"
        headers = {"Content-Type": "application/json"}
        if body.token:
            headers["Authorization"] = f"Bearer {body.token}"
        params = {"session_id": session_id}
        resp = requests.post(url, json={"mission_type": body.mission_type, "payload": payload}, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        intent_content = data.get("intent_content") or data.get("result") or data
        return {
            "intent": text,
            "intent_content": intent_content,
            "dem_response": data,
        }
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process_audio")
def process_audio():
    """
    Optional HTTP fallback: upload audio, return structured response.
    Not required for WebSocket flow; useful for CLI testing.
    """
    raise NotImplementedError("HTTP fallback not implemented in prototype.")


@app.websocket("/ws/avatar")
async def ws_avatar(ws: WebSocket):
    origin = ws.headers.get("origin", "")
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://nile-key.com",
    ]
    if not any(origin.startswith(allowed) for allowed in allowed_origins):
        await ws.close(code=1008)
        return

    await ws.accept()
    await ws.send_json({"type": "status", "text": "Initializing avatar layer..."})
    await ws.send_json({"type": "avatar_state", "state": "initializing"})

    session_id: str | None = None
    token: str | None = None

    try:
        prototype = AvatarPrototype()
        try:
            prototype.startup()
        except Exception as startup_exc:
            print(f"[server] AvatarPrototype startup skipped: {startup_exc}")
            prototype = None
    except Exception as exc:
        await ws.send_json({"type": "error", "text": f"Startup failed: {exc}"})
        await ws.send_json({"type": "avatar_state", "state": "error"})
        await ws.close()
        return

    await ws.send_json({"type": "status", "text": "Avatar ready. Send auth, then text."})
    await ws.send_json({"type": "avatar_state", "state": "ready"})

    audio_chunks: list[float] = []
    sample_rate = 16000
    recording = False
    SILENCE_THRESHOLD = 0.01
    SILENCE_DURATION_SAMPLES = int(1.5 * sample_rate)
    silence_counter = 0

    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data.get("type") == "auth":
                session_id = data.get("session_id") or DEM_SESSION_ID
                token = data.get("token")
                await ws.send_json({"type": "status", "text": "Authenticated."})
                await ws.send_json({"type": "avatar_state", "state": "ready"})
                continue

            if data.get("type") == "audio":
                chunk = data.get("data", [])
                if not chunk:
                    continue
                audio_chunks.extend(chunk)
                recording = True
                silence_counter = 0
                max_abs = max(abs(x) for x in chunk) if chunk else 0
                if max_abs < SILENCE_THRESHOLD:
                    silence_counter += len(chunk)
                else:
                    silence_counter = 0

                if silence_counter >= SILENCE_DURATION_SAMPLES and len(audio_chunks) > sample_rate * 0.5:
                    await _process_audio_chunks(ws, prototype, audio_chunks, sample_rate, session_id=session_id, token=token)
                    audio_chunks = []
                    recording = False
                    silence_counter = 0

            elif data.get("type") == "text":
                text = (data.get("text") or "").strip()
                if not text:
                    continue
                await ws.send_json({"type": "avatar_state", "state": "thinking"})
                await ws.send_json({"type": "transcript", "text": text})
                await _process_text_intent(ws, prototype, text, session_id=session_id, token=token)

            elif data.get("type") == "ice":
                pass

    except WebSocketDisconnect:
        print("[server] Client disconnected.")
    except Exception as exc:
        print(f"[server] Error: {exc}")
        try:
            await ws.send_json({"type": "error", "text": str(exc)})
        except Exception:
            pass


async def _process_audio_chunks(ws: WebSocket, prototype: AvatarPrototype, chunks: list[float], sample_rate: int, session_id: str | None = None, token: str | None = None) -> None:
    await ws.send_json({"type": "status", "text": "Transcribing..."})
    try:
        import numpy as np
        import scipy.io.wavfile as wavfile

        arr = np.array(chunks, dtype=np.float32)
        arr = np.clip(arr, -1.0, 1.0)
        arr_int16 = (arr * 32767).astype(np.int16)

        tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wavfile.write(tmp_wav.name, sample_rate, arr_int16)
        tmp_wav.close()

        if prototype is None:
            await ws.send_json({"type": "error", "text": "Audio path unavailable because AvatarPrototype failed to initialize."})
            await ws.send_json({"type": "avatar_state", "state": "error"})
            return
        pathlib.Path(tmp_wav.name).unlink(missing_ok=True)

        await ws.send_json({"type": "transcript", "text": result.get("intent", "")})
        text = result.get("intent", "")
        if text:
            await _process_text_intent(ws, prototype, text, session_id=session_id, token=token)
        await ws.send_json({"type": "status", "text": "Done."})
    except Exception as exc:
        await ws.send_json({"type": "error", "text": f"Audio processing failed: {exc}"})
        await ws.send_json({"type": "avatar_state", "state": "error"})


async def _process_text_intent(ws: WebSocket, prototype: AvatarPrototype, text: str, session_id: str | None = None, token: str | None = None) -> None:
    await ws.send_json({"type": "status", "text": "Processing intent..."})
    await ws.send_json({"type": "avatar_state", "state": "thinking"})
    try:
        response = send_intent_to_dem(text, session_id=session_id, token=token)
        intent_content = response.get("intent_content") or response.get("result") or response
        await ws.send_json({"type": "response", "text": str(intent_content)})
        await ws.send_json({"type": "avatar_state", "state": "responding"})
        await ws.send_json({"type": "status", "text": "Done."})
    except Exception as exc:
        await ws.send_json({"type": "error", "text": f"DEM call failed: {exc}"})
        await ws.send_json({"type": "avatar_state", "state": "error"})
