"""
Phase 8 E2E Acceptance Execution — Scenario 1: HTTP Simple Research with Evidence
Run: python tests/e2e/phase8_scenario1_http_research_evidence.py
"""

import os
import sys
import tempfile
import shutil
import uuid
from datetime import datetime, timezone

# Ensure backend is importable
sys.path.insert(0, r"F:\nilekey\nile-key-project\nile-key2\backend")

# Set minimal env before importing app modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-characters-1234567890")
os.environ.setdefault("ALLOWED_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("OWNER_PASSWORD", "TestOwnerPass123!")
os.environ["DISABLE_CSRF"] = "true"
os.environ["SEARCH_STUB_FALLBACK"] = "true"

from fastapi.testclient import TestClient
from app.core.config import settings
from main import app
from app.core.database import init_db


def main():
    # Isolated database setup (mirrors conftest.py behavior)
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "phase8_scenario1.db")
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite:///{db_path}"
    init_db()

    try:
        with TestClient(app) as client:
            base_url = "http://testserver"

            # 1. Register test user
            username = f"phase8_user_{uuid.uuid4().hex[:8]}"
            register_resp = client.post(
                f"{base_url}/api/v1/auth/register",
                json={
                    "email": f"{username}@example.com",
                    "username": username,
                    "full_name": "Phase 8 Test User",
                    "password": "TestPassword123!",
                    "phone": "+201000000000",
                    "company": "Phase8 Co",
                },
            )
            print(f"[1] Register: {register_resp.status_code}")
            assert register_resp.status_code == 200, f"Register failed: {register_resp.text}"

            # 1.5. Login as owner and approve the new user
            owner_login_resp = client.post(
                f"{base_url}/api/v1/auth/login",
                json={"username": "owner", "password": "TestOwnerPass123!"},
            )
            print(f"[1.5] Owner Login: {owner_login_resp.status_code}")
            assert owner_login_resp.status_code == 200, f"Owner login failed: {owner_login_resp.text}"
            owner_token = owner_login_resp.json()["access_token"]
            owner_headers = {"Authorization": f"Bearer {owner_token}"}

            # Get user_id from the registered user's email
            user_email = f"{username}@example.com"
            conn = __import__("sqlite3").connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
            row = cursor.fetchone()
            conn.close()
            user_id = row[0] if row else None
            assert user_id, f"User not found after registration: {user_email}"

            approve_resp = client.post(
                f"{base_url}/api/v1/users/{user_id}/approve?role=owner",
                headers=owner_headers,
                json={},
            )
            print(f"[1.6] Approve User: {approve_resp.status_code}")
            assert approve_resp.status_code == 200, f"Approve failed: {approve_resp.text}"

            # 2. Login with the new user
            login_resp = client.post(
                f"{base_url}/api/v1/auth/login",
                json={"username": username, "password": "TestPassword123!"},
            )
            print(f"[2] Login: {login_resp.status_code}")
            assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 3. Connect session
            connect_resp = client.post(
                f"{base_url}/api/v1/digital-export-manager/connect",
                headers=headers,
                json={"user_id": 1, "metadata": {"phase8": True}},
            )
            print(f"[3] Connect: {connect_resp.status_code}")
            assert connect_resp.status_code == 200, f"Connect failed: {connect_resp.text}"
            session_id = connect_resp.json()["session_id"]

            # 4. Create research mission with evidence
            mission_resp = client.post(
                f"{base_url}/api/v1/digital-export-manager/missions?session_id={session_id}",
                headers=headers,
                json={
                    "mission_type": "RESEARCH",
                    "payload": {
                        "query": "اريد تصدير الخضروات والفاكهة المصرية الى الاردن",
                        "context": {"session_id": session_id},
                        "decision_context": {
                            "research": {
                                "goal": "market study",
                                "status": "completed",
                                "findings": [
                                    {
                                        "topic": "trade flow",
                                        "content": "Egypt vegetable exports to Jordan increased 15% in 2024",
                                        "confidence": 0.9,
                                        "evidence": [
                                            {
                                                "source_id": "un-comtrade",
                                                "source_url": "https://comtrade.un.org",
                                                "content_excerpt": "HS code 07 vegetables Egypt→Jordan 2024",
                                                "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
                                            }
                                        ],
                                    }
                                ],
                                "sources_consulted": ["un-comtrade"],
                                "sources_failed": [],
                                "source_execution_statuses": {"un-comtrade": "SUCCESS_WITH_DATA"},
                            }
                        },
                    },
                },
            )
            print(f"[4] Create Mission: {mission_resp.status_code}")
            assert mission_resp.status_code == 200, f"Mission failed: {mission_resp.text}"
            mission_data = mission_resp.json()
            print(f"   Mission ID: {mission_data.get('mission_id')}")
            print(f"   Status: {mission_data.get('status')}")

            intent_content = mission_data.get("intent_content", {})
            print(f"   Intent Type: {intent_content.get('intent_type')}")

            business_answer = (intent_content.get("content") or {}).get("business_answer")
            print(f"   Business Answer present: {business_answer is not None}")

            if business_answer is None:
                print("[FAIL] business_answer is missing from intent_content")
                return False

            # 5. Validate business answer structure
            executive_summary = business_answer.get("executive_summary", "")
            key_findings = business_answer.get("key_findings", [])
            evidence = business_answer.get("evidence", [])
            sources = business_answer.get("sources", [])
            entities = business_answer.get("entities", [])
            opportunities = business_answer.get("opportunities", [])
            risks = business_answer.get("risks", [])
            recommendations = business_answer.get("recommendations", [])
            confidence = business_answer.get("confidence")
            limitations = business_answer.get("limitations", [])
            provenance = business_answer.get("provenance", {})
            coverage = provenance.get("coverage", {})
            comparisons = business_answer.get("comparisons")
            rankings = business_answer.get("rankings")

            print(f"   Executive Summary: {executive_summary[:200]}")
            print(f"   Key Findings count: {len(key_findings)}")
            print(f"   Evidence count: {len(evidence)}")
            print(f"   Sources: {sources}")
            print(f"   Entities: {entities}")
            print(f"   Opportunities: {opportunities}")
            print(f"   Risks: {risks}")
            print(f"   Recommendations count: {len(recommendations)}")
            print(f"   Confidence: {confidence}")
            print(f"   Limitations count: {len(limitations)}")
            print(f"   Coverage level: {coverage.get('coverage_level')}")
            print(f"   Comparisons: {comparisons}")
            print(f"   Rankings: {rankings}")

            # 6. Assertions per AC
            failures = []

            if not executive_summary or not isinstance(executive_summary, str):
                failures.append("AC-5: executive_summary missing or not string")

            if not key_findings or not isinstance(key_findings, list):
                failures.append("AC-4: key_findings missing or not list")

            if not evidence or not isinstance(evidence, list):
                failures.append("AC-13: evidence missing or not list")

            if not sources or not isinstance(sources, list):
                failures.append("AC-13: sources missing or not list")

            if not isinstance(entities, list):
                failures.append("AC-6: entities not list")

            if not isinstance(opportunities, list):
                failures.append("AC-7: opportunities not list")

            if not isinstance(risks, list):
                failures.append("AC-8: risks not list")

            if not isinstance(recommendations, list):
                failures.append("AC-9: recommendations not list")

            if confidence is not None and not isinstance(confidence, (int, float)):
                failures.append("AC-12: confidence not numeric or None")

            if not isinstance(limitations, list):
                failures.append("AC-14: limitations not list")

            if not provenance or not isinstance(provenance, dict):
                failures.append("AC-14: provenance missing or not dict")

            if coverage.get("coverage_level") not in ("adequate", "partial", "insufficient"):
                failures.append("AC-2: coverage_level invalid")

            if failures:
                print("\n[FAIL] Assertions failed:")
                for f in failures:
                    print(f"  - {f}")
                return False

            print("\n[PASS] All assertions passed for Scenario 1")
            return True

    finally:
        # Restore settings and cleanup temp database
        settings.DATABASE_URL = original_db_url
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
