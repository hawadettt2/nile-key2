# External Service Credential Management — Implementation Work Package

**WP ID:** 1787000000000-credential-management-impl
**Date:** 2026-08-16
**Status:** Draft — Pending Review/Approval
**Authority:** `.kilo/plans/1786845854881-external-service-credential-management.md` (APPROVED)
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`

---

## 1. Implementation Goal

Translate the approved Credential Management design into executable implementation steps for the DEM backend, creating a unified credential abstraction layer without modifying DEM Core contracts or expanding scope beyond the approved design.

---

## 2. Implementation Scope

| Component | Description |
|-----------|-------------|
| `Credential` abstraction | Abstract base class + concrete types: `ApiKeyCredential`, `UsernamePasswordCredential`, `ClientIdSecretCredential` |
| `CredentialStore` | Registry with `register()`, `get()`, `get_or_raise()`, `list_sources()`, `list_all()` |
| Masking/redaction | `mask()` implementation: first 4 chars visible if length > 4, else `***` |
| Source tracking | `source` field on every credential; populated at startup |
| Lifecycle hooks | `on_before_use()`, `on_after_use()`, `on_expiry()` |
| Adapter consumption | All external service adapters consume credentials via `CredentialStore` |
| FAOSTAT migration | Primary validation case; preserve JWT lifecycle exactly |
| Security enforcement | No raw credentials in adapters; no secrets in logs/errors; mandatory code review |

---

## 3. File Change Map

| File | Action | Phase |
|------|--------|-------|
| `backend/app/core/credentials/__init__.py` | Create | 1 |
| `backend/app/core/credentials/credential.py` | Create | 1 |
| `backend/app/core/credentials/credential_store.py` | Create | 1 |
| `backend/app/core/credentials/api_key_credential.py` | Create | 1 |
| `backend/app/core/credentials/username_password_credential.py` | Create | 1 |
| `backend/app/core/credentials/client_id_secret_credential.py` | Create | 1 |
| `backend/app/agent/knowledge/faostat_client.py` | Modify | 2 |
| `backend/app/agent/knowledge/faostat_provider.py` | Modify | 2 |
| `backend/main.py` | Modify | 2 |
| `backend/app/services/eta/eta_client.py` | Modify | 3 |
| `backend/app/services/shipping/letmeship_client.py` | Modify | 4 |
| `backend/app/services/shipping/sendcloud_client.py` | Modify | 4 |
| `backend/app/agent/knowledge/mooadapter_client.py` | Modify | 5 |
| `backend/app/agent/knowledge/mooadapter.py` | Modify | 5 |
| `backend/app/agent/knowledge/tradedata_client.py` | Modify | 5 |
| `backend/app/agent/knowledge/tradedata_provider.py` | Modify | 5 |
| `backend/app/agent/knowledge/zatca_client.py` | Modify | 5 |
| `backend/app/agent/knowledge/zatca_provider.py` | Modify | 5 |
| `backend/app/agent/knowledge/gccstat_client.py` | Modify | 5 |
| `backend/app/agent/knowledge/gccstat_provider.py` | Modify | 5 |
| `backend/app/core/smtp.py` (or equivalent) | Modify | 6 |
| `backend/app/agent/llm/provider.py` | Modify | 6 |

---

## 4. Implementation Phases

### Phase 1: Foundation — Credential Abstraction

**Goal:** Create `Credential` interface, concrete types, and `CredentialStore` with no adapter changes.

**Tasks:**
1. Create `backend/app/core/credentials/` package.
2. Implement `Credential` abstract base class with methods:
   - `get_type()`, `mask()`, `is_empty()`, `source()`
   - `on_before_use()`, `on_after_use()`, `on_expiry()`
3. Implement concrete types:
   - `ApiKeyCredential(key: str, source: str)`
   - `UsernamePasswordCredential(username: str, password: str, source: str)`
   - `ClientIdSecretCredential(client_id: str, client_secret: str, source: str)`
4. Implement `CredentialStore`:
   - `register(name, credential)`
   - `get(name) -> Optional[Credential]`
   - `get_or_raise(name) -> Credential`
   - `list_sources() -> Dict[str, str]`
   - `list_all() -> List[str]`
5. Implement masking logic:
   - Value length > 4: first 4 chars + `***`
   - Value length ≤ 4: `***`
6. Write unit tests for all credential types and `CredentialStore`.

**Acceptance Evidence:**
- All new files pass lint/typecheck.
- Unit tests for credential types pass.
- Unit tests for `CredentialStore` pass.
- No adapter files modified.
- No secrets in new code.

---

### Phase 2: FAOSTAT Migration (Primary Validation Case)

**Goal:** Migrate FAOSTAT to use `Credential` abstraction while preserving exact JWT lifecycle behavior.

**Tasks:**
1. Modify `FaostatApiClient.__init__` to accept `credential_store: CredentialStore`.
2. Modify `FaostatApiClient._login()` to:
   - Fetch credentials via `cred_store.get("faostat_username")` and `cred_store.get("faostat_password")`.
   - Call `credential.on_before_use()` before POST.
   - Call `credential.on_after_use()` after successful token acquisition.
   - If `cred_store.get()` returns `None`, log redacted warning and return without raising.
3. Modify `FaostatExternalSourceAdapter.__init__` to accept `credential_store: CredentialStore` instead of `username`/`password` in config dict.
4. Modify `backend/main.py` lifespan to:
   - Create `UsernamePasswordCredential` objects from `settings.FAOSTAT_USER` and `settings.FAOSTAT_PASSWORD`.
   - Register them in `CredentialStore` as `"faostat_username"` and `"faostat_password"`.
   - Pass `credential_store` to `FaostatExternalSourceAdapter`.
5. Preserve existing JWT lifecycle exactly:
   - 55-minute token expiry
   - `_ensure_token()` check before each request
   - 401 re-authentication retry (1 retry)
   - `_auth_lock` and `_re_auth_in_progress` concurrency protection
6. Do NOT introduce RefreshToken mechanism.

**Acceptance Evidence:**
- FAOSTAT unit tests (17) pass without modification.
- FAOSTAT integration tests (6) pass without modification.
- No raw credential strings in `faostat_client.py` or `faostat_provider.py`.
- All credential usage goes through `Credential` interface.
- `CredentialStore` is the single source of credentials for FAOSTAT.
- No RefreshToken code introduced.

---

### Phase 3: ETA Migration

**Goal:** Migrate ETA to use `ClientIdSecretCredential`.

**Tasks:**
1. Modify ETA client to accept `credential_store: CredentialStore`.
2. Create `ClientIdSecretCredential` objects in `main.py` lifespan from `settings.ETA_CLIENT_ID` and `settings.ETA_CLIENT_SECRET`.
3. Register as `"eta_client_id"` and `"eta_client_secret"` in `CredentialStore`.
4. Update adapter to fetch via `cred_store.get()`.
5. Apply `credential.mask()` in all ETA client logging.
6. Handle `None` from `cred_store.get()` gracefully.

**Acceptance Evidence:**
- ETA tests pass.
- No raw credential strings in ETA client files.
- Graceful degradation when credentials are absent.

---

### Phase 4: LetMeShip / SendCloud Migration

**Goal:** Migrate LetMeShip and SendCloud to use credential abstraction.

**Tasks:**
1. Modify LetMeShip client to accept `credential_store: CredentialStore`.
2. Modify SendCloud client to accept `credential_store: CredentialStore`.
3. Create `ApiKeyCredential` or appropriate credential objects in `main.py` lifespan.
4. Register in `CredentialStore`.
5. Update adapters to fetch via `cred_store.get()`.
6. Apply `credential.mask()` in all logging.

**Acceptance Evidence:**
- Shipping tests pass.
- No raw credential strings in shipping client files.

---

### Phase 5: Moaah / TradeData / ZATCA / GCC-Stat Migration

**Goal:** Bulk migrate simple API key adapters.

**Tasks:**
1. For each provider (Moaah, TradeData, ZATCA, GCC-Stat):
   - Modify client to accept `credential_store: CredentialStore`.
   - Modify provider to accept `credential_store: CredentialStore`.
   - Create `ApiKeyCredential` in `main.py` lifespan from settings.
   - Register in `CredentialStore`.
   - Update to fetch via `cred_store.get()`.
   - Apply `credential.mask()` in logging.
2. Handle `None` gracefully for all providers.

**Acceptance Evidence:**
- All knowledge provider tests pass.
- No raw credential strings in any knowledge client/provider files.

---

### Phase 6: SMTP / LLM Migration

**Goal:** Migrate SMTP and LLM configuration credentials.

**Tasks:**
1. Define `SmtpCredential` type or reuse existing types for SMTP configuration.
2. Modify SMTP client to accept `credential_store: CredentialStore`.
3. Modify LLM provider to accept `credential_store: CredentialStore`.
4. Create credentials in `main.py` lifespan.
5. Update to fetch via `cred_store.get()`.

**Acceptance Evidence:**
- SMTP/notification tests pass.
- LLM tests pass.
- No raw credential strings in SMTP/LLM files.

---

## 5. Security Implementation Details

### 5.1 No Raw Credentials in Adapters

- All adapter constructors accept `credential_store: CredentialStore`, never raw credential strings.
- Config dicts passed to adapters must not contain keys: `api_key`, `username`, `password`, `client_id`, `client_secret`, `api_id`, `api_password`.
- Enforced by mandatory code review.

### 5.2 Masking/Redaction

- Every credential type implements `mask()`:
  - Length > 4: first 4 characters + `***`
  - Length ≤ 4: `***`
- All logging in adapters/clients uses `credential.mask()` before output.
- No exception message contains raw credential values.

### 5.3 Source Tracking

- Every credential is created with `source="env"` (from environment injection).
- Future Secret Store integration will use different source values.
- `CredentialStore.list_sources()` provides audit mapping.
- `CredentialStore.list_all()` provides credential names for audit without values.

### 5.4 No Secrets in Git

- `config.py` Settings fields retain empty-string defaults.
- No new secret values added to any tracked file.
- `.env` remains gitignored.

---

## 6. Testing & Verification Strategy

### Per-Phase Testing

| Phase | Tests Required | Regression Checks | Security Checks | Acceptance Evidence |
|-------|---------------|-------------------|-----------------|---------------------|
| 1 | Unit tests for all Credential types and CredentialStore | None (no adapters changed) | Verify no secrets in new files | All unit tests pass; grep for secrets in new files returns none |
| 2 | FAOSTAT 17 unit + 6 integration tests | All existing FAOSTAT tests pass | No raw credentials in FAOSTAT files | Test report + grep evidence |
| 3 | ETA client tests | All existing ETA tests pass | No raw credentials in ETA files | Test report + grep evidence |
| 4 | Shipping tests | All existing shipping tests pass | No raw credentials in shipping files | Test report + grep evidence |
| 5 | Knowledge provider tests | All existing knowledge tests pass | No raw credentials in knowledge files | Test report + grep evidence |
| 6 | SMTP/LLM tests | All existing notification/LLM tests pass | No raw credentials in SMTP/LLM files | Test report + grep evidence |

### Global Regression

After all phases:
- Run full test suite.
- Verify no DEM Core test failures.
- Verify no KnowledgeProvider contract violations.
- Verify no raw credential strings in any migrated adapter file.

---

## 7. Acceptance Criteria

All criteria are evidence-based and verifiable.

### AC-1: Credential Abstraction Works
- [ ] `Credential` interface implemented with all required methods (`get_type`, `mask`, `is_empty`, `source`, `on_before_use`, `on_after_use`, `on_expiry`).
- [ ] Concrete types implemented for all credential categories used in the project.
- [ ] `CredentialStore` implemented with all required methods (`register`, `get`, `get_or_raise`, `list_sources`, `list_all`).

### AC-2: No Raw Credentials in Adapters
- [ ] No adapter `__init__` or config dict accepts raw credential strings.
- [ ] All adapters receive `CredentialStore` reference.

### AC-3: Masking/Redaction Effective
- [ ] `mask()` returns `***` for values ≤ 4 characters.
- [ ] `mask()` returns first 4 characters + `***` for values > 4 characters.
- [ ] No logging statement emits raw credential values.
- [ ] No exception message contains raw credential values.

### AC-4: Graceful Degradation on Missing Credentials
- [ ] When `cred_store.get()` returns `None`, adapters return empty results without raising.
- [ ] This behavior is verified for all migrated adapters.

### AC-5: Source Tracking Present
- [ ] Every credential has a `source` field populated at startup.
- [ ] `CredentialStore.list_sources()` returns correct mapping.
- [ ] `CredentialStore.list_all()` returns credential names without values.

### AC-6: FAOSTAT Lifecycle Preserved
- [ ] FAOSTAT JWT login flow unchanged.
- [ ] Token expiry (55 minutes) and re-authentication unchanged.
- [ ] Concurrent request protection (`_auth_lock`, `_re_auth_in_progress`) unchanged.
- [ ] No RefreshToken introduced.
- [ ] FAOSTAT unit tests (17) and integration tests (6) pass without modification.

### AC-7: No Hardcoded Secrets
- [ ] No credential values in source code.
- [ ] `config.py` Settings fields have empty-string defaults.
- [ ] No secrets added to tracked files.

### AC-8: DEM Core Unchanged
- [ ] `KnowledgeProvider` interface unchanged.
- [ ] `ReasoningEngine` unchanged.
- [ ] `KnowledgeProviderRegistry` unchanged.
- [ ] `KnowledgeOrchestrator` unchanged.
- [ ] No schema changes to `knowledge_nodes` or `knowledge_edges`.

### AC-9: No External Secret Store Dependency
- [ ] Implementation does not import or depend on any Secret Store product.
- [ ] Abstraction allows future Secret Store integration without adapter changes.

---

## 8. Scope Boundaries

This Implementation Work Package does NOT include:

- FAOSTAT Live Validation
- New external provider addition
- External Secret Store product selection or integration
- Database encryption for `eta_connectors.client_secret`
- Modification of `PLAN.md`
- Changes to DEM Core contracts
- Credential collection from users
- Any expansion beyond the approved design

---

## 9. Dependencies / Risks / Gates

### Dependencies

| Dependency | Status | Impact if Unresolved |
|------------|--------|----------------------|
| Approved design (1786845854881) | ✅ Approved | Implementation basis |
| FAOSTAT adapter implementation | ✅ Complete | Phase 2 target |
| Project Owner approval of this Implementation WP | 🔲 Pending | Execution cannot start |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Adapter developer bypasses CredentialStore | Medium | High | Mandatory code review; grep verification before gate |
| FAOSTAT tests fail after migration | Low | High | Phase 2 gate requires all tests passing before proceeding |
| CredentialStore becomes God object | Medium | Medium | Keep interface minimal; enforce single responsibility |
| Missing credential causes unexpected crash | Medium | Medium | Explicit `None` handling policy; graceful degradation requirement |

### Gates

| Gate | Phase | Criteria |
|------|-------|----------|
| G1 | Phase 1 → 2 | Foundation tests pass; no adapter files modified |
| G2 | Phase 2 → 3 | FAOSTAT tests (17 unit + 6 integration) pass; no raw credentials in FAOSTAT files |
| G3 | Phase 3 → 4 | ETA tests pass; no raw credentials in ETA files |
| G4 | Phase 4 → 5 | Shipping tests pass; no raw credentials in shipping files |
| G5 | Phase 5 → 6 | Knowledge provider tests pass; no raw credentials in knowledge files |
| G6 | Final | Full test suite passes; all acceptance criteria met |

---

## 10. Next Governance Step

**Status:** Draft — Pending Review/Approval

**Next Step:** Governance Review / Approval of this Implementation Work Package. Implementation does not begin until this WP is approved.

---

*Plan Status: Draft — Pending Review/Approval*
