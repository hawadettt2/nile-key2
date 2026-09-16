import asyncio
import json
import sys
import os

import websockets

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/avatar"


async def get_token():
    import requests
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "owner", "password": "TestOwnerPass123!"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


async def run_scenario2():
    token = await get_token()
    print(f"[1] Token obtained")

    async with websockets.connect(WS_URL, max_size=10_000_000) as ws:
        print("[2] WebSocket connected")

        auth_msg = {"type": "auth", "token": token, "session_id": None}
        await ws.send(json.dumps(auth_msg))
        auth_resp = await ws.recv()
        print(f"[3] Auth response: {auth_resp}")
        auth_data = json.loads(auth_resp)
        session_id = auth_data.get("session_id")
        assert session_id, "No session_id in auth response"

        arabic_request = "اريد تصدير الخضروات والفاكهة المصرية الى الاردن"
        text_msg = {"type": "text", "text": arabic_request}
        await ws.send(json.dumps(text_msg))
        print(f"[4] Sent Arabic request: {arabic_request}")

        thinking = await ws.recv()
        print(f"[5] Avatar thinking: {thinking}")
        thinking_data = json.loads(thinking)
        assert thinking_data.get("type") == "avatar_state"
        assert thinking_data.get("state") == "thinking"

        response_msg = await ws.recv()
        print(f"[6] Avatar response received")
        response_data = json.loads(response_msg)
        print(f"   Response type: {response_data.get('type')}")
        assert response_data.get("type") == "response"

        intent_content = json.loads(response_data.get("text", "{}"))
        print(f"   Intent type: {intent_content.get('intent_type')}")
        print(f"   Outcome: {intent_content.get('content', {}).get('outcome')}")

        business_answer = (intent_content.get("content") or {}).get("business_answer") or {}
        print(f"   Executive summary: {business_answer.get('executive_summary', '')[:200]}")
        print(f"   Key findings count: {len(business_answer.get('key_findings', []))}")
        print(f"   Evidence count: {len(business_answer.get('evidence', []))}")
        print(f"   Sources: {business_answer.get('sources', [])}")
        print(f"   Limitations count: {len(business_answer.get('limitations', []))}")

        responding = await ws.recv()
        responding_data = json.loads(responding)
        print(f"[7] Avatar state after response: {responding_data}")
        assert responding_data.get("type") == "avatar_state"
        assert responding_data.get("state") == "responding"

        failures = []
        if intent_content.get("intent_type") != "mission_completed":
            failures.append("intent_type is not mission_completed")
        if not business_answer.get("executive_summary"):
            failures.append("executive_summary missing")
        if not business_answer.get("key_findings"):
            failures.append("key_findings missing")
        if not business_answer.get("evidence"):
            failures.append("evidence missing")
        if not business_answer.get("sources"):
            failures.append("sources missing")

        if failures:
            print("\n[FAIL] Scenario 2 failed:")
            for f in failures:
                print(f"  - {f}")
            return False

        print("\n[PASS] Scenario 2 passed")
        return True


if __name__ == "__main__":
    ok = asyncio.run(run_scenario2())
    sys.exit(0 if ok else 1)
