# DEM Architecture Explorer v2 — Router Source-Level Reconciliation

Date: 2026-08-25

## Purpose

This is an evidence artifact for the Architecture Explorer graph. It records only source-level facts that have been verified. It does not modify application runtime behavior.

## Verified router source pattern

`backend/app/routers/auth.py` has been inspected directly.

- Router object: `router`
- Router type: FastAPI `APIRouter`
- Prefix: `/api/v1/auth`
- Tags: `Authentication`
- Endpoints verified in the inspected source: `POST /register`, `POST /login`, `POST /refresh`, `GET /me`, `PUT /me`, `POST /logout`
- Schemas directly referenced: `UserCreate`, `UserLogin`, `UserUpdate`, `User`, `Token`, `RegisterResponse`, `MessageResponse`
- Core/security dependencies directly referenced: `get_db`, `execute_update`, `verify_password`, `get_password_hash`, `create_access_token`, `create_refresh_token`, `decode_token`, settings
- Cross-cutting dependencies directly present: HTTPBearer, `Depends`, rate limiting, token blacklist
- Service dependency directly imported: `app.services.audit.log_audit` (the inspected excerpt establishes the import; invocation must be separately verified before creating a call edge)

## Runtime classification

The router's source-level existence and endpoint declarations are verified. Application-level registration must be proven separately from the router source itself. The graph therefore records source evidence and registration evidence as distinct facts.

## Required continuation

Repeat this exact reconciliation pattern for every router imported by `backend/main.py`, then reconcile each router's request/response schema and service/dependency call sites. Only after those records exist should endpoint-level runtime edges be promoted into the canonical graph.

## Non-negotiable rule

Do not infer service calls from imported names. An import proves dependency availability, not invocation. An invocation edge requires the actual call site in the source.
