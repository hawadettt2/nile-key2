# Project Owner Authorization — WP-42 UAT Account Creation and Password Reset

**Date:** 2026-08-03  
**Work Package:** WP-42 — Owner Acceptance / Release Validation  
**Authorization Type:** UAT Account Creation and Password Reset  
**Status:** ACTIVE

---

## Authorization Statement

I, as Project Owner, hereby authorize the creation of the following UAT accounts for the exclusive purpose of executing the Manual Browser UAT for WP-42.

### Authorized Accounts

| Username | Role | Purpose |
|----------|------|---------|
| `uat_owner` | `owner` | Test full owner permissions |
| `uat_manager` | `manager` | Test manager permissions |
| `uat_sales` | `sales` | Test sales/user permissions |

### Password Policy

- **Format:** 6-digit numeric passwords
- **Scope:** These accounts only
- **Lifetime:** Until WP-42 closure
- **Storage:** Not to be committed to repository

### Authorized Actions

1. Create the above accounts via the application's standard registration mechanism
2. Verify login functionality for each account
3. Use these accounts exclusively for WP-42 Manual Browser UAT

### Password Reset Authorized

**Password Reset Authorized:** Yes

**Scope:** Allow password reset for `uat_owner`, `uat_manager`, and `uat_sales` to 6-digit numeric values, as needed for WP-42 Manual Browser UAT only.

### Restrictions

- These accounts are for UAT only
- Do not use for production or other purposes
- Do not commit passwords to repository
- Delete or disable after WP-42 closure

---

## Project Owner Endorsement

I, as Project Owner, confirm that this document represents a formal authorization for UAT account creation and password reset.

**Accounts Approved:**
- `uat_owner` — Role: `owner`
- `uat_manager` — Role: `manager`
- `uat_sales` — Role: `sales`

**Password Policy Approved:** 6-digit numeric passwords for the above accounts only.

**Password Reset Approved:** Yes — for the above accounts only, as needed for WP-42 Manual Browser UAT.

**Purpose Confirmed:** These accounts are authorized exclusively for Manual Browser UAT execution for WP-42.

**Storage Policy Confirmed:** Actual passwords shall not be stored in the repository.

| Field | Value |
|-------|-------|
| Project Owner Name | Osama hosny |
| Signature | Osama hosny |
| Date | 2026-08-03 |
| Witness (optional) | _______________ |

---

## Verification

| Item | Status |
|------|--------|
| Accounts created | ? Done |
| Login verified | ? Done |
| Password reset authorized | ? Done |
| UAT completed | Pending |

---

## Sign-off

| Field | Value |
|-------|-------|
| Project Owner Name | Osama hosny |
| Signature | Osama hosny |
| Date | 2026-08-03 |
| Witness (optional) | _______________ |

---

*This document authorizes UAT account creation and password reset only. It does not authorize any code changes, database modifications beyond account creation and password reset, or closure of any WP-42 gates.*
