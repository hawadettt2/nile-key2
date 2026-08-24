# External Service Credential Management — Work Package Plan

**Plan ID:** 1786845854881-external-service-credential-management
**Date:** 2026-08-16
**Status:** Draft — Pending Review/Approval
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md`, `PLAN.md` (Master Roadmap v2.1)
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
**Scope Boundary:** `backend/app/core/config.py`, `backend/main.py`, all `backend/app/agent/knowledge/*_client.py`, `backend/app/agent/knowledge/*_provider.py`

---

## 1. Goal & Scope

### 1.1 Goal

Create a **unified, abstraction-layer Credential/Secret Management** for all external services consumed by DEM, ensuring no provider-specific credential handling logic is duplicated or scattered across adapters and the application bootstrap.

### 1.2 In Scope

| Component | Description |
|-----------|-------------|
| Credential abstraction interface | Define a provider-agnostic credential contract that all external service adapters consume |
| Credential type taxonomy | Support: API Key, Username/Password, Client ID/Secret, and extensible future types |
| Credential lifecycle hooks | Define hooks for `login`, `expiry`, `refresh` where the external service requires them |
| Runtime source resolution | Define how credentials are sourced at runtime without assuming a specific Secret Store product |
| Hardcoding prevention | Enforce that no credential is ever hardcoded in adapter code |
| Log safety | Enforce that no credential value is ever emitted in log output |
| Masking/redaction | Enforce that any credential representation in errors, diagnostics, or responses is redacted |
| Rotation/rollover policy | Define the rotation policy and hook points |
| Migration path for existing providers | Define the step-by-step migration for Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, ETA, LetMeShip, SendCloud, SMTP, LLM |

### 1.3 Out of Scope

| Item | Reason |
|------|--------|
| Implementation of any code | This is a planning artifact only |
| Migration execution | No migration is performed in this plan |
| New external provider addition | No new provider is added in this plan |
| FAOSTAT live validation | No live API calls are made in this plan |
| External Secret Store product selection | Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, etc. are NOT assumed or selected |
| DEM Core expansion | KnowledgeProvider interface, ReasoningEngine, ToolOrchestrator, and all DEM core contracts remain untouched |
| PLAN.md modification | PLAN.md is not modified |
| Credential requests from user | No credentials are requested or collected |

---

## 2. Current Problem

### 2.1 What `BaseSettings + .env` Actually Is

`BaseSettings` via `pydantic_settings` is a **configuration loader**. It reads environment variables and `.env` files into a `Settings` singleton. It provides:
- Typed access to environment variables
- Default values
- Basic validation (`model_post_init`)

It does **not** provide:
- Secret encryption at rest
- Secret rotation
- Secret versioning
- Credential type abstraction
- Credential lifecycle management
- Source attribution (which environment injected this value vs. which secret store)
- Masking/redaction utilities
- Structured credential objects

### 2.2 Current Credential Flow

```
.env file
  → pydantic_settings.BaseSettings
    → settings singleton (plain strings)
      → main.py lifespan bootstrap
        → raw credential values injected into adapter config dict
          → adapter stores them as plain instance attributes
            → HTTP client uses them directly
```

### 2.3 Symptoms of the Problem

| Symptom | Location | Impact |
|---------|----------|--------|
| Credentials stored as plain `TEXT` in `eta_connectors` table | `backend/app/core/database.py:570` | No encryption at rest for ETA connector secrets |
| Credentials passed as raw `config` dicts | `backend/main.py:86-193` | No abstraction; each adapter handles credentials differently |
| FAOSTAT stores `username` and `password` as plain instance attributes | `backend/app/agent/knowledge/faostat_client.py:33-34` | Token lifecycle is client-specific; no shared pattern |
| No masking/redaction in logs or error messages | All adapters | Risk of credential leakage in logs |
| No rotation policy or hook | All adapters | No mechanism to rotate credentials without restart |
| No source tracking | All adapters | Cannot distinguish env-var-injected from secret-store-injected credentials |
| `.env` files present in working directory (gitignored) | Root, `backend/` | Acceptable for local dev but no structured escalation path to production secret management |

### 2.4 Root Cause

There is **no Credential Management Layer** between `Settings` and the adapters. Each adapter independently handles its own credential acquisition, storage, and usage. This creates:
- Duplication of credential handling logic
- Inconsistent security posture across adapters
- No centralized place to add rotation, masking, or source tracking
- FAOSTAT's JWT token lifecycle is embedded in the client, not abstracted

---

## 3. Functional Requirements

### FR-1: Credential Abstraction Interface

Define a `Credential` interface that represents a credential regardless of its type. The interface must support:

```python
class Credential(ABC):
    @abstractmethod
    def get_type(self) -> str          # "api_key", "username_password", "client_id_secret", ...
    @abstractmethod
    def mask(self) -> str              # Returns a masked representation for logs/diagnostics
    @abstractmethod
    def is_empty(self) -> bool         # Whether the credential has a usable value
    @abstractmethod
    def source(self) -> str            # "env", "vault", "aws_secrets_manager", etc.
    @abstractmethod
    async def on_before_use(self) -> None   # Lifecycle hook called before credential is used
    @abstractmethod
    async def on_after_use(self) -> None    # Lifecycle hook called after credential is used
    @abstractmethod
    async def on_expiry(self) -> None       # Lifecycle hook called when credential expires
```

Concrete implementations:
- `ApiKeyCredential(key: str, source: str)` — for Moaah, TradeData, ZATCA, GCC-Stat, LLM
- `UsernamePasswordCredential(username: str, password: str, source: str)` — for FAOSTAT
- `ClientIdSecretCredential(client_id: str, client_secret: str, source: str)` — for ETA, SendCloud

### FR-2: Credential Type Taxonomy

| Type | Fields | Used By |
|------|--------|---------|
| `api_key` | `key` | Moaah, TradeData, ZATCA, GCC-Stat, LLM, SearXNG |
| `username_password` | `username`, `password` | FAOSTAT |
| `client_id_secret` | `client_id`, `client_secret` | ETA, SendCloud |
| `basic_auth` | `api_id`, `api_password` | LetMeShip |
| `smtp` | `host`, `port`, `user`, `password` | SMTP |

### FR-3: Credential Lifecycle Hooks

| Hook | Trigger | Behavior |
|------|---------|----------|
| `on_before_use` | Before each HTTP request or auth call | Verify credential is still valid; trigger refresh if needed |
| `on_after_use` | After successful use | Update last-used timestamp; log (redacted) usage |
| `on_expiry` | Credential expires (e.g., JWT token TTL) | Trigger re-authentication or rotation |

**Note:** `on_expiry` is only relevant for time-limited credentials (FAOSTAT JWT token). Static API keys do not have expiry in the current architecture.

### FR-4: Masking/Redaction

- `mask()` must return a string that reveals at most the first 4 characters, replacing the rest with `***`.
- If the credential value is 4 characters or shorter, the entire value is masked as `***` (no characters are revealed).
- No credential value, partial value, or derived value may appear in:
  - `logging` output at any level
  - Exception messages
  - HTTP response bodies
  - Diagnostic endpoints
  - Debug prints

### FR-5: Source Tracking

Every `Credential` instance carries a `source` field:
- `"env"` — injected via environment variable / `.env` file
- `"vault"` — injected via HashiCorp Vault (future)
- `"aws_secrets_manager"` — injected via AWS Secrets Manager (future)
- `"azure_key_vault"` — injected via Azure Key Vault (future)

The source is used for:
- Audit logging (redacted)
- Rotation policy enforcement
- Environment-specific behavior

### FR-6: Rotation/Rollover Policy

Define a rotation policy interface:

```python
class RotationPolicy(ABC):
    @abstractmethod
    async def should_rotate(self, credential: Credential) -> bool:
    @abstractmethod
    async def rotate(self, credential: Credential) -> Credential:
    @abstractmethod
    def max_age_days(self) -> int:
```

Default policy: **static credentials do not auto-rotate**. Rotation is triggered only by:
- Explicit admin action
- External secret store version change event
- Expiry hook for time-limited credentials (FAOSTAT token re-auth)

### FR-7: Credential Registry / Store

Define a `CredentialStore` that holds all resolved credentials for the application lifetime:

```python
class CredentialStore:
    def register(self, name: str, credential: Credential) -> None
    def get(self, name: str) -> Optional[Credential]
    def get_or_raise(self, name: str) -> Credential
    def list_sources(self) -> Dict[str, str]   # name → source
    def list_all(self) -> List[str]            # registered credential names only, no values
```

The store is populated during `main.py` lifespan startup and is read-only thereafter.

---

## 4. Security Requirements

### SR-1: No Hardcoding

- No credential value may appear in source code.
- No default credential values in `Settings` fields that are intended for production secrets.
- All `Settings` fields that hold credentials must have empty-string defaults (`""`).
- Any adapter that receives a credential must receive it via the `Credential` interface, never as a raw string parameter.
- Adapters must not accept raw credential strings in constructor parameters or config dict values. This must be verified by mandatory code review during implementation. If feasible within project tooling, a lint rule or type-checking constraint must be added to prevent raw credential strings from being passed to adapter constructors.

### SR-2: No Credential Logging

- The `mask()` method must be applied to any credential representation before it is logged.
- Logging statements must use `%s` formatting with `credential.mask()`, never the raw value.
- Exception handlers must not include raw credential values in exception messages.

### SR-3: Masking/Redaction in Errors and Diagnostics

- Any error returned to the client must not contain credential values.
- Any diagnostic endpoint must redact credential values.
- Stack traces captured in production must be scrubbed of credential values.

### SR-4: Rotation/Rollover Policy

- Static credentials (API keys, client secrets): rotation is manual/admin-triggered.
- Time-limited credentials (FAOSTAT JWT): automatic re-authentication on expiry.
- No credential is cached beyond its valid lifetime.
- When a credential is rotated, all in-flight requests using the old credential must complete before the new credential takes effect.

### SR-5: Runtime Source Specification

- At startup, the runtime must record the source of each credential (env, vault, etc.).
- This record is used for audit and for determining rotation behavior.
- If no source can be determined, the credential is treated as `"env"` (the lowest-trust source).

---

## 5. Integration Design

### 5.1 Adapter Consumption Pattern

Current pattern (before):
```python
# main.py
faostat_adapter = FaostatExternalSourceAdapter(config={
    "username": settings.FAOSTAT_USER,    # raw string
    "password": settings.FAOSTAT_PASSWORD, # raw string
})
```

Target pattern (after):
```python
# main.py lifespan
cred_store = CredentialStore()
cred_store.register("faostat_username", UsernamePasswordCredential(
    username=settings.FAOSTAT_USER,
    password=settings.FAOSTAT_PASSWORD,
    source="env",
))
# faostat_adapter receives cred_store reference; fetches credentials via interface
faostat_adapter = FaostatExternalSourceAdapter(
    credential_store=cred_store,
    config={...non-sensitive config...},
)
```

### 5.2 Adapter Changes

Each adapter must:
1. Accept a `CredentialStore` reference instead of raw credential values in its config dict.
2. Fetch credentials via `credential_store.get("provider_credential_name")`.
3. If `credential_store.get()` returns `None`, treat the credential as absent and degrade gracefully (return empty results, do not raise).
4. Apply `credential.mask()` in any log or error message.
5. Call `credential.on_before_use()` before each HTTP request.
6. Call `credential.on_after_use()` after each successful HTTP request.

### 5.3 Config Changes

`config.py` (`Settings` class) must:
- Keep all credential fields as plain strings loaded from environment (this is the injection point).
- Add no new secrets or default values.
- Remain the single point of environment injection.
- The translation from `Settings` fields to `Credential` objects happens in `main.py` lifespan.

### 5.4 main.py Changes

`main.py` `lifespan()` must:
- After `settings` is loaded, construct `CredentialStore`.
- For each external service, create typed `Credential` objects from `settings` fields and register them in the store.
- Pass `credential_store` to each adapter constructor.
- Log (redacted) credential source for each service.

### 5.5 Preservation of Existing Contracts

| Contract | Preservation Requirement |
|----------|-------------------------|
| `KnowledgeProvider` interface | Unchanged |
| `FaostatExternalSourceAdapter.query()` return shape | Unchanged |
| `FaostatExternalSourceAdapter.get_sources()` return shape | Unchanged |
| `KnowledgeProviderRegistry` | Unchanged |
| `KnowledgeOrchestrator` | Unchanged |
| `ReasoningEngine` | Unchanged |
| DEM Core (memory, tools, session, approval) | Unchanged |

---

## 6. FAOSTAT-Specific Requirements

### 6.1 Preserve Existing Behavior

FAOSTAT's current JWT authentication lifecycle in `faostat_client.py` must be **preserved exactly**:

1. `POST /auth/login` with username/password → receives JWT Bearer token
2. Token stored in-memory, expires after 55 minutes (hardcoded TTL below 60-minute API TTL)
3. `_ensure_token()` checks expiry before each request; re-authenticates if expired
4. 401 response triggers re-authentication and retry (1 retry)
5. Concurrent requests protected by `_auth_lock` and `_re_auth_in_progress` flag

### 6.2 FAOSTAT as Primary Validation Case

FAOSTAT is the **primary validation case** for the new Credential Management Layer because:
- It is the only adapter with a time-limited credential (JWT token with expiry).
- It has the most complex credential lifecycle (`login → token → expiry → re-login`).
- It is already implemented and tested (17 unit tests + 6 integration tests).
- Its `username/password → automatic login → token lifecycle` pattern must remain functional after migration.

### 6.3 No RefreshToken Assumption

- The current implementation does **not** use OAuth2 refresh tokens.
- The FAOSTAT JWT re-authentication is implemented as `re-login with username/password`, not as `refresh_token` grant.
- The new Credential Management Layer must **not** introduce a RefreshToken mechanism for FAOSTAT.
- Any "refresh" behavior for FAOSTAT must continue to use the existing `re-login` pattern.

### 6.4 FAOSTAT Credential Migration

FAOSTAT's `UsernamePasswordCredential` must:
- Provide `username` and `password` via the `Credential` interface.
- The `FaostatApiClient` must receive the credential object and call `credential.on_before_use()` before `_login()` and `credential.on_after_use()` after successful token acquisition.
- Token expiry and re-authentication logic remains in `FaostatApiClient`; the credential object does not manage the token.

---

## 7. Deployment / Runtime Secret Management

### 7.1 Environment Injection vs. Secret Store

| Dimension | Environment Injection (`env` / `.env`) | Secret Store (Vault, AWS SM, etc.) |
|-----------|----------------------------------------|------------------------------------|
| Source | OS environment variables, `.env` files | Dedicated secrets management service |
| Lifetime | Process lifetime | Independent of process; supports versioning |
| Rotation | Requires process restart | Supported via polling/webhook/event |
| Access control | OS-level | Fine-grained, audit-logged |
| Audit trail | OS audit logs | Dedicated secrets audit log |
| Current usage | All credentials in this project | **None — not in scope for this WP** |

### 7.2 Minimum Required Now

The **minimum required now** is:
1. Credential abstraction layer (`Credential` interface + concrete types).
2. `CredentialStore` as the single point of credential access for adapters.
3. Masking/redaction enforcement.
4. Source tracking (`source` field on each `Credential`).
5. Lifecycle hooks (`on_before_use`, `on_after_use`, `on_expiry`).

No external Secret Store product is required or assumed. The abstraction must be designed so that a Secret Store backend can be plugged in later without changing adapter code or DEM Core contracts.

### 7.3 Future Secret Store Integration Path

When a Secret Store product is selected (decision outside this WP's scope):
1. Implement a `VaultCredential` / `AwsSecretsManagerCredential` that fetches the secret value at `on_before_use` time.
2. The `source` field is set to the product name.
3. Adapters and DEM Core are unaffected.

---

## 8. Migration Path for Existing Services

### 8.1 Phase Order

Migration must proceed in this order to minimize risk:

| Phase | Target | Rationale |
|-------|--------|-----------|
| 1 | `Credential` interface + `CredentialStore` | Foundation; no adapter changes yet |
| 2 | FAOSTAT | Most complex lifecycle; primary validation case |
| 3 | ETA | Client ID/Secret type; different from FAOSTAT |
| 4 | LetMeShip, SendCloud | Basic auth / API key types |
| 5 | Moaah, TradeData, ZATCA, GCC-Stat | Simple API key types; bulk migration |
| 6 | SMTP, LLM | Configuration credentials; last because they are less critical |

### 8.2 Per-Provider Migration Checklist

For each provider, the migration must:

1. Replace raw credential fields in adapter `__init__` with `CredentialStore` reference.
2. Create typed `Credential` object in `main.py` lifespan from `settings`.
3. Register credential in `CredentialStore` with a unique name.
4. Update adapter to fetch credentials via `cred_store.get(name)`.
5. Apply `credential.mask()` in all logging within the adapter.
6. Verify existing tests pass with the new credential flow.
7. Verify adapter still returns empty results when credentials are absent (graceful degradation).

### 8.3 FAOSTAT Migration Example (Primary Validation Case)

FAOSTAT is the primary validation case for the Credential Management Layer due to its time-limited JWT token lifecycle. The following steps preserve existing behavior exactly:

1. In `main.py` lifespan, create `UsernamePasswordCredential` objects from `settings.FAOSTAT_USER` and `settings.FAOSTAT_PASSWORD` and register them in `CredentialStore` with unique names (e.g., `"faostat_username"`, `"faostat_password"`).
2. Modify `FaostatExternalSourceAdapter.__init__` to accept `credential_store: CredentialStore` instead of `username`/`password` in the config dict.
3. Modify `FaostatApiClient.__init__` to accept `credential_store: CredentialStore` and fetch credentials via `cred_store.get("faostat_username")` and `cred_store.get("faostat_password")`.
4. In `FaostatApiClient._login()`, call `credential.on_before_use()` before the POST and `credential.on_after_use()` after successful token acquisition. If `cred_store.get()` returns `None`, log a redacted warning and return without raising.
5. Preserve existing JWT token lifecycle exactly: 55-minute expiry, `_ensure_token()`, 401 re-authentication retry, `_auth_lock`, and `_re_auth_in_progress` concurrency protection.
6. Do not introduce any RefreshToken mechanism. Re-authentication must continue to use `username/password` re-login.
7. Verify all 17 existing unit tests and 6 integration tests pass without modification.

---

## 9. Acceptance Criteria

All acceptance criteria must be verifiable without executing code (evidence-based review).

### AC-1: Credential Abstraction Interface Defined

- [ ] `Credential` abstract interface is specified with all required methods.
- [ ] Concrete implementations are specified for each credential type used in the project.
- [ ] `mask()` behavior is specified for each type (first 4 chars visible, rest `***`).

### AC-2: No Raw Credential Strings in Adapter Configs

- [ ] No adapter `__init__` accepts raw credential strings as config dict values.
- [ ] All adapters receive `CredentialStore` reference instead.

### AC-3: No Credential Leakage in Logs or Errors

- [ ] No logging statement in any adapter or client can emit a raw credential value.
- [ ] No exception message in any adapter or client can contain a raw credential value.
- [ ] `mask()` method is applied before any credential reaches a logging or error path.

### AC-4: FAOSTAT Token Lifecycle Preserved

- [ ] FAOSTAT JWT login flow is specified to remain unchanged.
- [ ] Token expiry (55 minutes) and re-authentication behavior is specified to remain unchanged.
- [ ] Concurrent request protection (`_auth_lock`, `_re_auth_in_progress`) is specified to remain unchanged.
- [ ] No RefreshToken mechanism is introduced for FAOSTAT.
- [ ] Existing FAOSTAT unit tests (17) and integration tests (6) pass after migration without modification.

### AC-5: Credential Source Tracked

- [ ] Every `Credential` instance carries a `source` field.
- [ ] The source is populated at startup from the injection mechanism.
- [ ] The source is available for audit without exposing the credential value.

### AC-6: Rotation Policy Defined

- [ ] Rotation policy interface is specified.
- [ ] Default behavior for static credentials (no auto-rotation) is specified.
- [ ] Re-authentication behavior for time-limited credentials (FAOSTAT) is specified.

### AC-7: No Hardcoding

- [ ] No credential default values exist in `Settings` for production secrets.
- [ ] No credential values appear in source code.
- [ ] All credential fields in `Settings` have empty-string defaults.

### AC-8: Adapter Migration Path Documented

- [ ] Migration order is specified (Phase 1–6).
- [ ] Per-provider migration checklist is specified.
- [ ] No DEM Core changes are required for any migration step.

### AC-9: External Secret Store Not Assumed

- [ ] No specific Secret Store product is named or assumed in the design.
- [ ] The abstraction is designed to allow future Secret Store integration without adapter changes.
- [ ] The minimum required implementation does not depend on any external Secret Store.

### AC-10: DEM Core Unchanged

- [ ] `KnowledgeProvider` interface is unchanged.
- [ ] `ReasoningEngine` is unchanged.
- [ ] `KnowledgeProviderRegistry` is unchanged.
- [ ] `KnowledgeOrchestrator` is unchanged.
- [ ] No changes to `knowledge_nodes` or `knowledge_edges` schema.

---

## 10. Evidence / Validation Plan

### 10.1 Evidence Collection

| Evidence | Source | How to Verify |
|----------|--------|---------------|
| Credential interface specification | This plan | Read plan Section 3 |
| No raw credential strings in adapter configs | Code review | Grep for `settings.*_KEY`, `settings.*_SECRET`, `settings.*_PASSWORD`, `settings.*_USER` in adapter files |
| No credential leakage in logs | Code review | Grep for `logger.*(.*settings\..*KEY\|.*SECRET\|.*PASSWORD\|.*USER)` in adapter files |
| FAOSTAT token lifecycle preserved | Code review + test review | Compare `faostat_client.py` before/after migration; verify 17 unit tests + 6 integration tests still pass |
| Credential source tracked | Code review | Verify `source` field on all `Credential` implementations |
| Rotation policy defined | Plan review | Read plan Section 4, SR-4 |
| No hardcoding | Code review | Grep for credential default values in `config.py`; verify all are `""` |
| DEM Core unchanged | Diff review | Verify no changes to `KnowledgeProvider`, `ReasoningEngine`, `KnowledgeProviderRegistry` |

### 10.2 Validation Gates

| Gate | Criteria | Evidence Required |
|------|----------|-------------------|
| G0 | Plan reviewed and approved | Project Owner approval record in plan |
| G1 | Credential interface specification complete and reviewed | Signed-off interface spec in plan |
| G2 | Adapter migration plan complete for all 6 phases | Migration checklist in plan |
| G3 | Security requirements verified against current code | Grep evidence + manual review |
| G4 | FAOSTAT behavior preservation verified | Test suite evidence |
| G5 | No DEM Core changes required | Diff review |

---

## 11. Dependencies & Risks

### 11.1 Dependencies

| Dependency | Status | Impact if Unresolved |
|------------|--------|----------------------|
| FAOSTAT adapter implementation complete | ✅ Complete (WP-38a–38d closed) | FAOSTAT migration would be speculative |
| `Credential` interface design | 🔲 Pending this plan | No implementation can proceed |
| Project Owner approval of this plan | 🔲 Pending | Implementation cannot start |
| Selection of external Secret Store product (future) | 🔲 Out of scope | Abstraction must be designed to be pluggable regardless |

### 11.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Adapter developers bypass `CredentialStore` and use raw strings | Medium | High | Enforce via code review; add lint rule if feasible |
| `mask()` implementation is inconsistent across types | Low | Medium | Specify exact masking behavior in interface contract |
| FAOSTAT token lifecycle breaks during migration | Low | High | FAOSTAT is Phase 2; validate against existing tests before moving to Phase 3 |
| CredentialStore becomes a God object | Medium | Medium | Keep interface minimal; `CredentialStore` only stores and retrieves |
| External Secret Store selection changes abstraction requirements | Low | Low | Design abstraction to be backend-agnostic from the start |
| `eta_connectors.client_secret` plaintext in DB not addressed | Medium | Medium | This plan defines the abstraction; DB encryption is a separate concern |

---

## 12. What Is Outside the Scope of This Work Package

| Item | Reason |
|------|--------|
| Implementation of any code | This is a planning artifact only |
| Execution of any migration | Migration is defined in the plan; execution is a separate WP |
| FAOSTAT live API validation | No live calls; FAOSTAT is the validation case, not a test target |
| New external provider addition | No new provider is added |
| External Secret Store product selection | Decision deferred; abstraction is product-agnostic |
| DEM Core contract changes | KnowledgeProvider, ReasoningEngine, and all DEM core interfaces remain unchanged |
| Database encryption for `eta_connectors.client_secret` | Separate concern; this WP defines the application-layer abstraction only |
| PLAN.md modification | PLAN.md is the master roadmap; this plan is subordinate |
| Credential requests from user | No credentials are collected or requested |

---

## 13. Summary — Governance Checklist

```
WP Created → Scope → Acceptance Criteria → Dependencies → Out of Scope → Next Governance Step
```

**WP Created:** This document — External Service Credential Management Work Package Plan.

**Scope:** Unified credential abstraction layer for all external services; adapter migration path; FAOSTAT token lifecycle preservation; no external Secret Store assumption; no DEM Core changes.

**Acceptance Criteria:** 10 criteria defined in Section 9 (AC-1 through AC-10), all verifiable via code review and test evidence without executing new code.

**Dependencies:** FAOSTAT implementation complete (✅); this plan approved (🔲); Project Owner approval (🔲).

**Out of Scope:** Code implementation, migration execution, FAOSTAT live validation, new providers, external Secret Store selection, DEM Core changes, PLAN.md modification, credential collection.

**Next Governance Step:** **Review and Approval of this Work Package Plan** by Project Owner. Implementation does not begin until this plan is approved and a separate Implementation Work Package is created and approved.

---

*Plan Status: Draft — Pending Review/Approval*
