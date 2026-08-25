# DEM Architecture Explorer v2 — API / Core / Security Reconciliation

Date: 2026-08-25

## Scope

Evidence reconciliation only. No application runtime behavior is changed.

## API / Router evidence

`backend/main.py` is confirmed as the FastAPI application entry point and imports the router modules below:

- auth
- shipping
- invoice
- suppliers
- customers
- customs
- resources
- documents
- eta
- notifications
- audit
- workflow
- digital_export_manager_router
- knowledge_graph
- trade_intelligence
- dashboard
- search
- users_router
- roles_router
- research
- export_readiness

The import list is direct repository evidence that these router modules participate in application assembly. The graph must not infer endpoint-level relationships until each router's exact APIRouter declaration and registration call are reconciled.

## Core evidence

`backend/main.py` directly imports and initializes:

- `app.core.config.settings`
- `app.core.database.init_db`
- `app.core.csrf.CSRFMiddleware`
- ETA scheduler lifecycle
- shipping scheduler lifecycle
- `CredentialStore`
- credential types for username/password, client id/secret, and API key
- `SQLiteMemoryProvider`

It also installs `SecurityHeadersMiddleware` and configures CORS/rate-limit dependencies at the application boundary.

## Runtime vs configured/conditional status

The graph must distinguish:

- application-boundary infrastructure that is unconditionally installed;
- infrastructure initialized during lifespan;
- provider registrations conditional on environment configuration;
- components merely importable from the repository.

For example, LLM registration is conditional on `settings.LLM_API_KEY`; SMTP credentials are conditional on SMTP configuration; external knowledge adapters are conditionally registered when their required configuration is present. These are not equivalent to unconditional runtime components.

## Security evidence

The application boundary explicitly includes:

- CORS middleware
- CSRF middleware import/configuration
- rate-limit handler dependencies
- security response headers
- credential-store based secret registration

Security must remain a cross-cutting concern in the graph and must not be represented as a business capability.

## Credential boundary

Credentials are represented through `CredentialStore` and typed credential objects rather than treating raw secrets as architecture nodes. The graph should record the credential abstraction, its registration points, and its source classification (`env` where established), but never store secret values.

## Scheduler boundary

ETA and shipping schedulers are explicit application lifecycle infrastructure. They must be represented as schedulers/background infrastructure, not as ordinary business-service calls.

## Reconciliation limitation

The current pass establishes application-level router imports and core/security bootstrap evidence. Exact endpoint-to-service edges, individual router APIRouter declarations, schema identities, and every middleware registration still require source-level reconciliation before canonical graph merge.

## Acceptance rule for this slice

No edge is promoted to `primary_runtime` merely because a module is imported. Runtime edges require the actual registration/initialization/call site as evidence.
