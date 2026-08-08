"""
WP-42 Task 2: Manual UAT Execution — Automated Verification Script
This script executes UAT items via API and documents results.
Manual browser verification items are noted as requiring human verification.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = []
DEFECTS = []

def log_result(category, item, result, notes=""):
    RESULTS.append({
        "category": category,
        "item": item,
        "result": result,  # PASS, FAIL, N/A
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    })

def log_defect(category, item, description, severity="Medium"):
    DEFECTS.append({
        "category": category,
        "item": item,
        "description": description,
        "severity": severity
    })

# Test user credentials
TEST_USER = {"username": "uat_test", "password": "TestPass123!"}
access_token = None
refresh_token = None

print("=" * 60)
print("WP-42 Task 2: Manual UAT Execution")
print("=" * 60)
print(f"Start Time: {datetime.now().isoformat()}")
print()

# ==========================================
# Authentication Tests
# ==========================================
print("## Authentication Tests ##")

# Test 1: Login with valid credentials
try:
    response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER, timeout=10)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        log_result("Authentication", "Login with valid credentials", "PASS", "Returns 200 with tokens")
    else:
        log_result("Authentication", "Login with valid credentials", "FAIL", f"Status: {response.status_code}")
        log_defect("Authentication", "Login", f"Expected 200, got {response.status_code}")
except Exception as e:
    log_result("Authentication", "Login with valid credentials", "FAIL", str(e))
    log_defect("Authentication", "Login", str(e))

# Test 2: Login with invalid credentials
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    }, timeout=10)
    if response.status_code in [401, 422]:
        log_result("Authentication", "Login with invalid credentials", "PASS", f"Returns {response.status_code}")
    else:
        log_result("Authentication", "Login with invalid credentials", "FAIL", f"Expected 401/422, got {response.status_code}")
        log_defect("Authentication", "Invalid credentials", f"Expected 401/422, got {response.status_code}")
except Exception as e:
    log_result("Authentication", "Login with invalid credentials", "FAIL", str(e))

# Test 3: Protected endpoint without token
try:
    response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
    if response.status_code in [401, 403]:
        log_result("Authentication", "Protected endpoint without token", "PASS", f"Returns {response.status_code}")
    else:
        log_result("Authentication", "Protected endpoint without token", "FAIL", f"Expected 401/403, got {response.status_code}")
except Exception as e:
    log_result("Authentication", "Protected endpoint without token", "FAIL", str(e))

# Test 4: Protected endpoint with valid token
if access_token:
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/dashboard", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Authentication", "Protected endpoint with valid token", "PASS", "Returns 200 with data")
        else:
            log_result("Authentication", "Protected endpoint with valid token", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Authentication", "Protected endpoint with valid token", "FAIL", str(e))

# ==========================================
# API Endpoints Tests
# ==========================================
print("\n## API Endpoints Tests ##")

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health", timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "healthy":
            log_result("API", "GET /health", "PASS", "Returns healthy status")
        else:
            log_result("API", "GET /health", "FAIL", f"Status: {data.get('status')}")
    else:
        log_result("API", "GET /health", "FAIL", f"Status: {response.status_code}")
except Exception as e:
    log_result("API", "GET /health", "FAIL", str(e))

# Test openapi.json
try:
    response = requests.get("http://localhost:8000/openapi.json", timeout=10)
    if response.status_code == 200:
        log_result("API", "GET /openapi.json", "PASS", "Returns valid schema")
    else:
        log_result("API", "GET /openapi.json", "FAIL", f"Status: {response.status_code}")
except Exception as e:
    log_result("API", "GET /openapi.json", "FAIL", str(e))

# ==========================================
# Business Workflow Tests
# ==========================================
print("\n## Business Workflow Tests ##")

if access_token:
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test suppliers
    try:
        response = requests.get(f"{BASE_URL}/suppliers", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Suppliers", "GET /suppliers list", "PASS", "Returns 200")
        else:
            log_result("Suppliers", "GET /suppliers list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Suppliers", "GET /suppliers list", "FAIL", str(e))
    
    # Test customers
    try:
        response = requests.get(f"{BASE_URL}/customers", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Customers", "GET /customers list", "PASS", "Returns 200")
        else:
            log_result("Customers", "GET /customers list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Customers", "GET /customers list", "FAIL", str(e))
    
    # Test shipments
    try:
        response = requests.get(f"{BASE_URL}/shipments", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Shipments", "GET /shipments list", "PASS", "Returns 200")
        else:
            log_result("Shipments", "GET /shipments list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Shipments", "GET /shipments list", "FAIL", str(e))
    
    # Test invoices
    try:
        response = requests.get(f"{BASE_URL}/invoices/", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Invoices", "GET /invoices/ list", "PASS", "Returns 200")
        else:
            log_result("Invoices", "GET /invoices/ list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Invoices", "GET /invoices/ list", "FAIL", str(e))
    
    # Test documents
    try:
        response = requests.get(f"{BASE_URL}/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Documents", "GET /documents list", "PASS", "Returns 200")
        else:
            log_result("Documents", "GET /documents list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Documents", "GET /documents list", "FAIL", str(e))
    
    # Test resources
    try:
        response = requests.get(f"{BASE_URL}/resources", headers=headers, timeout=10)
        if response.status_code == 200:
            log_result("Resources", "GET /resources list", "PASS", "Returns 200")
        else:
            log_result("Resources", "GET /resources list", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_result("Resources", "GET /resources list", "FAIL", str(e))

# ==========================================
# Summary
# ==========================================
print("\n" + "=" * 60)
print("UAT EXECUTION SUMMARY")
print("=" * 60)

total = len(RESULTS)
passed = sum(1 for r in RESULTS if r["result"] == "PASS")
failed = sum(1 for r in RESULTS if r["result"] == "FAIL")
na = sum(1 for r in RESULTS if r["result"] == "N/A")

print(f"Total Tests Executed: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Not Applicable: {na}")
print()

if DEFECTS:
    print("## Defects Found ##")
    for i, defect in enumerate(DEFECTS, 1):
        print(f"{i}. [{defect['severity']}] {defect['category']} - {defect['item']}: {defect['description']}")
else:
    print("No defects found.")

print()
print(f"End Time: {datetime.now().isoformat()}")

# Save results
with open("uat_results.json", "w") as f:
    json.dump({"results": RESULTS, "defects": DEFECTS}, f, indent=2)

print("\nResults saved to uat_results.json")
