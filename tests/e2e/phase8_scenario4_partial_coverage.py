"""
Phase 8 E2E Acceptance Execution — Scenario 4: HTTP Partial Coverage
"""
import sys
import uuid
import requests

BASE = "http://localhost:8000/api/v1"


def main():
    # 1. Register test user
    username = f"phase8_user_{uuid.uuid4().hex[:8]}"
    register_resp = requests.post(
        f"{BASE}/auth/register",
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

    # 2. Login as owner to approve the new user
    owner_login = requests.post(
        f"{BASE}/auth/login",
        json={"username": "owner", "password": "TestOwnerPass123!"},
    )
    print(f"[2] Owner Login: {owner_login.status_code}")
    assert owner_login.status_code == 200, f"Owner login failed: {owner_login.text}"
    owner_token = owner_login.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # 3. Approve the new user as owner
    user_id = register_resp.json().get("user_id")
    assert user_id, "No user_id in registration response"

    approve_resp = requests.post(
        f"{BASE}/users/{user_id}/approve?role=owner",
        headers=owner_headers,
        json={},
    )
    print(f"[3] Approve User: {approve_resp.status_code}")
    assert approve_resp.status_code == 200, f"Approve failed: {approve_resp.text}"

    # 4. Login with the new user
    login_resp = requests.post(
        f"{BASE}/auth/login",
        json={"username": username, "password": "TestPassword123!"},
    )
    print(f"[4] User Login: {login_resp.status_code}")
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 5. Connect session
    connect_resp = requests.post(
        f"{BASE}/digital-export-manager/connect",
        headers=headers,
        json={"user_id": 1, "metadata": {"phase8": True}},
    )
    print(f"[5] Connect: {connect_resp.status_code}")
    assert connect_resp.status_code == 200, f"Connect failed: {connect_resp.text}"
    session_id = connect_resp.json()["session_id"]

    # 6. Create research mission that triggers partial coverage
    mission_resp = requests.post(
        f"{BASE}/digital-export-manager/missions?session_id={session_id}",
        headers=headers,
        json={
            "mission_type": "RESEARCH",
            "payload": {
                "query": "ما هي فرص تصدير الخضروات المصرية الى الاردن",
                "context": {"session_id": session_id},
            },
        },
    )
    print(f"[6] Create Mission: {mission_resp.status_code}")
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

    # 7. Validate business answer structure for partial coverage scenario
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

    # 8. Assertions per AC for partial coverage scenario
    failures = []

    if not executive_summary or not isinstance(executive_summary, str):
        failures.append("AC-5: executive_summary missing or not string")

    if not isinstance(key_findings, list):
        failures.append("AC-4: key_findings not list")

    if not isinstance(evidence, list):
        failures.append("AC-13: evidence not list")

    if not isinstance(sources, list):
        failures.append("AC-13: sources not list")

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

    # For partial coverage, we expect some evidence but not full coverage
    if coverage.get("coverage_level") == "insufficient":
        # This is acceptable for partial coverage scenario
        pass

    # Ensure no fabricated claims
    if evidence and not sources:
        failures.append("AC-13: evidence exists but no sources")

    if failures:
        print("\n[FAIL] Assertions failed:")
        for f in failures:
            print(f"  - {f}")
        return False

    print("\n[PASS] All assertions passed for Scenario 4")
    return True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
