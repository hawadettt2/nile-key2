# WP-42 Manual UAT Runbook

**Version:** 1.0  
**Date:** 2026-07-22  
**Baseline:** ebc2181  
**Project:** Nile Key Platform  
**Work Package:** WP-42 — Owner Acceptance  

---

## 1. Pre-UAT Checklist

### Environment
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Database initialized (`nile_key.db`)
- [ ] Test data loaded (suppliers, customers, shipments, etc.)
- [ ] No existing sessions/cookies

### Credentials
| Role | Username | Password |
|------|----------|----------|
| Owner | (to be provided) | (to be provided) |
| Manager | (to be provided) | (to be provided) |
| User | (to be provided) | (to be provided) |

### Tools
- [ ] Browser with DevTools (Chrome/Firefox)
- [ ] Screenshot tool ready
- [ ] Network tab enabled
- [ ] Console tab enabled
- [ ] Evidence directory ready: `.kilo/plans/wp42-uat-evidence/`

---

## 2. UAT Execution Order

Execute in this exact order:

### Phase 1: Authentication (Critical Path)
1. Login with valid credentials
2. Login with invalid credentials
3. Session persistence
4. Token expiration
5. Logout

### Phase 2: RBAC
1. Owner access to all pages
2. Manager access limitations
3. User access limitations
4. Unauthorized access redirect

### Phase 3: Input Validation
1. Required fields validation
2. Format validation
3. Empty states
4. Error messages

### Phase 4: Business Workflows
1. Supplier CRUD
2. Customer CRUD + CSV import
3. Shipment management
4. Invoice management
5. Customs declarations
6. Document management
7. ETA operations
8. Notifications
9. Workflows

### Phase 5: Data Integrity
1. CRUD operations persistence
2. Data relationships
3. Cascade deletes
4. Audit logging

### Phase 6: Error Handling
1. 400 errors
2. 401 errors
3. 403 errors
4. 404 errors
5. 500 errors
6. Network errors

### Phase 7: Performance
1. Page load times
2. API response times
3. Large dataset handling

### Phase 8: Security
1. CSRF protection
2. CORS headers
3. Security headers
4. Rate limiting
5. Cookie security

### Phase 9: Mobile/Responsive
1. Desktop (1920x1080)
2. Laptop (1366x768)
3. Tablet (768x1024)
4. Mobile (375x667)

### Phase 10: Final Acceptance
1. Overall system review
2. Defect review
3. Sign-off

---

## 3. Evidence Requirements Per Item

For **each** UAT item:

### Required Evidence
1. **Screenshot** - Full page showing the result
2. **Network Request** - API call showing request/response
3. **Console Output** - Showing no errors (or errors if testing error handling)

### Evidence Naming
`{area}-{item-id}-{type}.{ext}`

Examples:
- `auth-01-login-success.png`
- `auth-02-login-failure.png`
- `rbac-01-owner-access.png`

### Failed Items
If a test fails:
1. Take screenshot of the failure
2. Capture error message
3. Document reproduction steps
4. Link to related WP if applicable

---

## 4. Pass/Fail Criteria

| Result | Criteria |
|--------|----------|
| **PASS** | Item behaves as documented in UAT_CHECKLIST.md |
| **FAIL** | Item does not behave as documented |
| **N/A** | Item not applicable to this deployment |
| **BLOCKED** | Cannot test due to external dependency |

---

## 5. Defect Management

If a FAIL is encountered:
1. Document the defect in the Defect Log
2. Determine severity: Critical / High / Medium / Low
3. Link to affected Work Package
4. If Critical or High: UAT session stops, WP is reopened
5. If Medium or Low: Continue UAT, document for later fix

---

## 6. Completion Criteria

UAT is complete when:
- [ ] All 255 items executed
- [ ] All items marked PASS, N/A, or BLOCKED
- [ ] No Critical or High defects remain open
- [ ] Evidence collected for each item
- [ ] Evidence index created

---

## 7. Post-UAT Steps

1. Review all evidence with Project Owner
2. Complete Owner Acceptance Certificate
3. Project Owner signs certificate
4. Update governance documents
5. Create closure report
6. Git commit and push

---

## 8. Important Notes

- **No assumptions:** If unsure, mark as FAIL and document
- **User perspective:** Test as an actual end user, not as a developer
- **Objective evidence:** Every pass/fail must have evidence
- **Project Owner authority:** Project Owner has final say on acceptance
- **No skipping:** All items must be executed

---

*Runbook Version: 1.0*  
*Approved by: _________________*  
*Date: _________________*
