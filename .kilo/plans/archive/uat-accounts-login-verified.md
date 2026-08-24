# UAT Account Login Verification â€” API-Based

## Verification Method

Login verification was performed via API call to `POST /api/v1/auth/login` for each UAT account.

## Results

| Username | Role | Password | HTTP Status | access_token | refresh_token |
|----------|------|----------|-------------|--------------|---------------|
| uat_owner | owner | 6-digit numeric | 200 OK | âœ… Present | âœ… Present |
| uat_manager | manager | 6-digit numeric | 200 OK | âœ… Present | âœ… Present |
| uat_sales | sales | 6-digit numeric | 200 OK | âœ… Present | âœ… Present |

## Evidence

- Authorization: `\.kilo/plans/archive/1785629497292-uat-account-creation-authorization\.md`
- Accounts verified: 2026-08-03
- Method: API-based verification (not browser-based UAT)

## Notes

- This is API-based verification, not Manual Browser UAT
- Manual Browser UAT-01 still requires human execution per `docs/appendices/wp42-uat-runbook.md`
- Passwords are not disclosed per security policy

