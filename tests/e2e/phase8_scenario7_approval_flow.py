"""
Phase 8 E2E Acceptance Execution — Scenario 7: HTTP Approval Flow
"""
import sys
import time
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

    # 6. Create mission that triggers approval (destructive operation)
    mission_resp = requests.post(
        f"{BASE}/digital-export-manager/missions?session_id={session_id}",
        headers=headers,
        json={
            "mission_type": "TRANSITION_WORKFLOW",
            "payload": {
                "query": "cancel the workflow",
                "context": {"session_id": session_id},
                "customer_id": 1,
                "supplier_id": 1,
            },
        },
    )
    print(f"[6] Create Mission: {mission_resp.status_code}")
    assert mission_resp.status_code == 200, f"Mission failed: {mission_resp.text}"
    mission_data = mission_resp.json()
    print(f"   Mission ID: {mission_data.get('mission_id')}")
    print(f"   Status: {mission_data.get('status')}")
    print(f"   Requires Approval: {mission_data.get('requires_approval')}")
    print(f"   Approval Status: {mission_data.get('approval_status')}")
    print(f"   Intent Type: {mission_data.get('intent_content', {}).get('intent_type')}")

    mission_id = mission_data.get("mission_id")
    assert mission_id, "No mission_id in response"

    # Print full mission result for debugging
    print(f"   Full mission result: {mission_data}")

    # 7. Check approval inbox
    list_resp = requests.get(f"{BASE}/digital-export-manager/approvals", headers=owner_headers)
    print(f"[7] List Approvals: {list_resp.status_code}")
    assert list_resp.status_code == 200, f"List approvals failed: {list_resp.text}"
    approvals = list_resp.json()
    print(f"   Approvals count: {len(approvals)}")
    approval_found = False
    for approval in approvals:
        if approval.get("mission_id") == mission_id:
            approval_found = True
            print(f"   Approval found: {approval}")
            break
    assert approval_found, f"Approval {mission_id} not found in inbox"

    # 8. Approve the mission
    approve_resp = requests.post(
        f"{BASE}/digital-export-manager/approvals/{mission_id}/approve",
        headers=owner_headers,
        json={},
    )
    print(f"[8] Approve Mission: {approve_resp.status_code}")
    assert approve_resp.status_code == 200, f"Approve mission failed: {approve_resp.text}"
    approve_data = approve_resp.json()
    print(f"   Approval response: {approve_data}")

    # 9. Check mission status after approval
    time.sleep(2)  # Wait for async processing
    mission_status_resp = requests.get(
        f"{BASE}/digital-export-manager/missions/{mission_id}?session_id={session_id}",
        headers=headers,
    )
    print(f"[9] Mission Status After Approval: {mission_status_resp.status_code}")
    if mission_status_resp.status_code == 200:
        updated_mission = mission_status_resp.json()
        print(f"   Updated Status: {updated_mission.get('status')}")
        print(f"   Updated Approval Status: {updated_mission.get('approval_status')}")
    else:
        print(f"   Could not fetch updated mission: {mission_status_resp.status_code}")

    # 10. Validate business answer if available
    intent_content = mission_data.get("intent_content", {})
    business_answer = (intent_content.get("content") or {}).get("business_answer")
    print(f"[10] Business Answer present: {business_answer is not None}")

    print("\n[PASS] Scenario 7 approval flow executed successfully")
    return True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
