# Gate D — Avatar Prototype

Self-hosted prototype proving Avatar works atop existing Core AI, without new intelligence.

## Stack (from Gate C)

| Component | Version | Role |
|-----------|---------|------|
| LiveTalking | v2.0.4 | Avatar video + WebRTC |
| MuseTalk | v1.5 | Lip-sync engine |
| Whisper | v20250625 | Speech-to-Text |
| SILMA TTS | v1 (2026-03-13) | Arabic + English TTS |

All components are open-source and self-hosted. No commercial API keys or per-minute fees.

## Architecture

```
Browser (WebRTC + mic)
  <-> WS /ws/avatar
  <-> Avatar Interaction Layer (this prototype)
       -> Whisper (local STT)
       -> DEM /missions API (existing Core AI)
       -> SILMA TTS (local TTS)
       -> LiveTalking (local avatar video)
  <-> LiveTalking server (port 8010)
       -> MuseTalk (lip-sync)
       -> Browser WebRTC
```

## Prerequisites

- Python 3.10+
- GPU with CUDA (recommended: NVIDIA RTX 4090 or similar)
- LiveTalking server installed and running (default: `http://127.0.0.1:8010`)
- DEM backend running (default: `http://127.0.0.1:8001`)
- Optional: MuseTalk model weights if LiveTalking is configured to use MuseTalk backend

## Installation

```bash
# From repo root
pip install fastapi uvicorn websockets openai-whisper torch requests scipy numpy

# SILMA TTS
pip install silma-tts

# LiveTalking
git clone https://github.com/lipku/LiveTalking.git
cd LiveTalking
pip install -r requirements.txt
# Download model weights per LiveTalking README
```

## Configuration

Edit `config/avatar.yaml` or set environment variables:

```bash
export DEM_API_BASE_URL="http://127.0.0.1:8001/api/v1/digital-export-manager"
export DEM_SESSION_ID="demo-session-001"
export LIVETALKING_URL="http://127.0.0.1:8010"
export LIVETALKING_AVATAR_ID="wav2lip256_avatar1"
export WHISPER_MODEL="small"
export SILMA_TTS_MODEL="silma-ai/silma-tts"
```

## Start LiveTalking (separate terminal)

```bash
cd LiveTalking
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1
```

## Start Avatar Interaction Layer

```bash
python -m prototype.avatar-interaction-layer.server
```

Server runs on `http://0.0.0.0:8020`.

## Use Prototype

1. Open `http://localhost:8020/` in browser (Chrome/Edge recommended for WebRTC).
2. Click **Start Voice** and allow microphone.
3. Speak Arabic text, e.g.:
   > أريد تصدير الخضر والفواكه المصرية إلى الأردن.
4. Watch transcript and avatar response.

### Text fallback

If voice is unavailable, type directly in the browser console:

```js
ws.send(JSON.stringify({ type: 'text', text: 'أريد تصدير الخضر والفواكه المصرية إلى الأردن.' }));
```

## Expected Flow

1. Browser captures audio -> WebSocket -> Avatar layer
2. Whisper transcribes Arabic audio -> text
3. Text sent to DEM `/missions` with `payload.query`
4. Core AI processes through Reasoning -> Knowledge -> Decision -> Plan -> Mission -> Task -> Execution
5. `IntentContent` returned to Avatar layer
6. SILMA TTS synthesizes Arabic speech from response text
7. Audio sent to LiveTalking for lip-sync + avatar video
8. Avatar video streamed back to browser via WebRTC

## Notes

- This is a prototype. Production would require VAD, error recovery, session management, and proper WebRTC signaling.
- LiveTalking health is checked at startup; if unavailable, audio/TTS still works but avatar video is skipped.
- MuseTalk Arabic quality depends on upstream audio from SILMA TTS; fine-tuning may be required.
- DEM API must be reachable; no changes to DEM core are required.
