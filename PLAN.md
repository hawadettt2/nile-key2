# Master Roadmap v2.1 � ���� ����� ����� �������
# Nile Key Digital Platform � Master Roadmap v2.1

**�������:** 2026-07-26
**�������:** 2.1.0
**������:** Constitution � authoritative reference for the lifetime of the project
**������:** ���� ����� ����� ��������� �������� ������� �.�.�
**������:** ����� �������� ������� (���ѡ ����ɡ ������ ������)
**�������:** ����� ������ �� ���� ��������� �������
**������:** ������ ��� ���� ����� ������� ������ ���������� �������� �������
**�������:** nile-key.com

---

# ����� ������

��� ������� �� ������� ������ �������.

�� ����� ��� ��� ����� ���� �����.

�� ����� ����� �������.

�� ����� ������ ������� ���� ������.

�� ���� ���� �� ����� �� ������ MUST ����� ��� �����.

---

# 1. ������ ������������

**������:** ���� ����� ����� ��������� �������� ������� �.�.�
**������:** ����� �������� ������� (���ѡ ����ɡ ������ ������)
**�������:** ����� ������ �� ���� ��������� �������
**������:** ������ ��� ���� ����� ������� ������ ���������� �������� �������
**�������:** nile-key.com

����� ������� NOT �� ���� ERP ���.
����� �� ������� ���� ������� ������� �� ����� ������ ������ ������ ������ ������� ���� ���� ������ ������.

������� �������� ��������:
1. `erpnext_egypt_compliance` (Axentorllc) � ���� �������� ������� ������
2. `erpnext-shipping` (frappe) � ���� ����� �����

---

# 2. ������ ��� ������� �������

1. ? �� Frappe Framework
2. ? �� ERPNext
3. ? �� MariaDB/Redis/Bench
4. ? �� ����� ���� �����
5. ? Frontend ����� 100% ��� GitHub Pages
6. ? Backend ���� ����� ��� Docker / PythonAnywhere Free
7. ? ������� ���� HTTP/API �� ������� Frappe ������ ������
8. ? ����� �����/�������� (RTL)
9. ? ������ ����� ������ ��� ������� (Docker + �����)

---

# 3. ��������� �������

```
???????????????????????????????????????????
?         GitHub Pages / Docker            ?
?     (React App - Static Hosting)         ?
?           nile-key.com                   ?
????????????????????????????????????????????
                     ?
           ???????????????????????
           ?    API Gateway       ?
           ?   FastAPI Backend    ?
           ?   Docker / PA Free   ?
           ???????????????????????
                     ?
       ???????????????????????????????
       ?              ?              ?
??????????  ???????????  ???????????
?Shipping?  ? ETA     ?  ? Customs ?
?Engine  ?  ? Engine  ?  ? Engine  ?
?(SQLite)?  ?(SQLite) ?  ?(SQLite) ?
??????????  ???????????  ???????????
       ?              ?              ?
       ???????????????????????????????
                     ?
           ???????????????????????
           ?   Core Services      ?
           ?  - Auth/Roles        ?
           ?  - Suppliers         ?
           ?  - Customers         ?
           ?  - Documents         ?
           ?  - Resources         ?
           ????????????????????????
```

## 3.1 ��������

| ������ | ������� |
|--------|---------|
| Frontend | React 18 + Vite + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite (MVP) ? PostgreSQL (Production) |
| Auth | JWT (PyJWT) + bcrypt |
| HTTP Client | httpx (Backend) + axios (Frontend) |
| Validation | Pydantic (Backend) |
| State | Zustand + React Query |
| i18n | i18next (ar/en) |
| Charts | Recharts |
| Tables | TanStack Table |
| Containerization | Docker + Docker Compose |

## 3.2 ������� ������� (8 Services MVP � 12+ Services Full)

### 3.2.1 Shipping Engine
- ��������: /api/v1/shipping/rates, /shipments, /track/{id}, /label
- ������ �������: CRUD + ����� + ���� ������
- ������� ������: ����� ����� �� LetMeShip � SendCloud

### 3.2.2 ETA Engine
- ��������: /api/v1/invoices, /validate, /cancel, /status
- ������ �������: CRUD + ���� ����� ����
- ������� ������: ����� ����� �� ETA (����� ����ڡ ���ڡ ������ PDF)

### 3.2.3 Customs Engine
- ��������: /api/v1/customs/declarations, /hs-codes, /calculate-duties
- ������ �������: ? ���� ������� �� ���� ���� ������

### 3.2.4 Suppliers Service
- ��������: /api/v1/suppliers (CRUD + certificates)
- ������ �������: ? ���� �������

### 3.2.5 Customers/Importers Service
- ��������: /api/v1/customers (CRUD + import CSV)
- ������ �������: ? ���� �������

### 3.2.6 Documents & Templates Service
- ��������: /api/v1/documents/templates, /generate, /upload
- ������ �������: ? ���� �������

### 3.2.7 Auth & Roles Service
- ��������: /api/v1/auth/login, /register, /refresh, /me
- �������: Owner, Manager, Sales, Admin Staff, Accountant, Logistics, Supplier, Customer
- ������ �������: ? ���� �������

### 3.2.8 Resources & Opportunities Service
- ��������: /api/v1/resources, /search
- ������ �������: ? ���� �������

## 3.3 ����� �������� � �������

- users, roles, suppliers, customers, shipments, invoices, customs_declarations, hs_codes, documents, resources
- ������: ������� ������� ���� ������ �������. Phase 1.5 ����� ����� ETA � Shipping ��������.

## 3.4 ����� ����� ��������

1. ������� ������ `init_db()` ��� ��� �������
2. `init_db()` ���� ������� �� ��� �����ɡ ����� ������� ������� ��� `_ensure_*_schema()`� ������ �������� �������
3. ��� ��� ���� ������� Alembic ������� ������ ������� �������

---

# 4. ������

- JWT: access_token (24h) + refresh_token (7d)
- CORS: ���� �� `ALLOWED_ORIGINS` �� ���������
- SECRET_KEY: ����� �� �����ɺ ���� ������� ��� �����
- Rate Limiting: ����� ��� ��� ���� ������
- File Upload: max 10MB
- CSRF: middleware ����� ������� ��� mutated

---

# 5. ���������

- **Frontend:** GitHub Pages �� Docker/Nginx
- **Backend:** Docker Compose �� PythonAnywhere Free Tier

---

# 6. Business Capability Map

## 6.1 �����

��� ������ �� ����� ������� ���� �� perspective ������� ��������.

## 6.2 ������� ��������

| # | ������ | ����� | ������� | ������ |
|---|--------|-------|---------|--------|
| 1 | ETA Compliance | ������ ����� ���� - ����� ��������ɡ ������ʡ ����� ����ڡ ���� | ETA Engine | ?? ��� ���� |
| 2 | Shipping Management | ����� ������� - ����ѡ ������ �����ʡ ���� | Shipping Engine | ?? ��� ���� |
| 3 | Customs Clearance | ������� ������� - ������ʡ ����� HS� ���� ���� | Customs Engine | ? ���� |
| 4 | Supplier Management | ����� �������� - �����ʡ �����ʡ ����� | Suppliers Service | ? ���� |
| 5 | Customer Management | ����� ������� - �����ʡ ������� CSV� ����� | Customers Service | ? ���� |
| 6 | Invoice Management | ����� �������� - ������ ���ޡ ����� | ETA Engine (��������) | ?? ���� |
| 7 | Document Management | ����� ������� - ��ڡ ����ȡ ��� | Documents Service | ? ���� |
| 8 | Export Operations | ������ ������� - ����ޡ ������ʡ ��� | Resources + Customs | ?? ���� |
| 9 | Trade Intelligence | ���� ����� - ����� ������ʡ ������� | Phase 2 | ? ���� |
| 10 | Knowledge Graph | ��� ����� - ������ ������ �����ʡ ������ | Phase 2 | ? ���� |
| 11 | Digital Export Manager | ���� ��� - ����ϡ �������ʡ ������� | Phase 2 | ? ���� |
| 12 | AI Memory | ����� ������ - ������ʡ ������ ����� | Phase 2 | ? ���� |
| 13 | Opportunity Discovery | ������ ��� - ����� ����ɡ ����� | Phase 2 | ? ���� |
| 14 | Market Analysis | ����� ����� - �����ѡ ������� | Phase 2 | ? ���� |
| 15 | Supplier Intelligence | ���� �������� - ����� �������� | Phase 2 | ? ���� |
| 16 | Buyer Intelligence | ���� ������� - ���ߡ ������ | Phase 2 | ? ���� |
| 17 | Administration | ����� ������ - �������� ������ʡ ������� | Auth + Core | ? ���� |
| 18 | Reports & Dashboard | �����ѡ ����� ����ɡ �������� | Dashboard | ?? ���� |
| 19 | Audit & Compliance | ��� ����ޡ ������ ���� �������� | Audit Logs | ?? ���� |
| 20 | Notifications | ������� - ���� �������� ������� | Notification Service | ?? ��� ���� |

---

# 7. ����� ������ � ���� ����

## ������� 1: ������ ? (�����)
- WP-01: ���� ������� ����� FastAPI
- WP-02A�H: ����� ���� ����� ��������
- WP-03: ����� ����� ���� ��������
- WP-04: ������ �� ����� CRUD
- WP-05: ������� ���� �������
- WP-06: �������� �������
- WP-07: ����� ������ (SECRET_KEY, CORS)
- WP-08: ����� ������ (.env, execute_update)
- WP-09: ����� ����� ����� ������ ���������
- WP-10: ���� ����� Alembic
- WP-11: ����� �������
- WP-12: Docker hardening
- WP-13A: ������� ���� �������� ��������
- WP-15: ������� ���� ���� �������� ��� ���� �������
- WP-16B: ���� ������� ��������
- WP-17A: �������� ���� �������
- WP-17B: �������� ���� �������
- WP-18: ������� ������� ������

## ������� 1.5: ����� ������ ���� ������� (������ � ������)
- WP-19: ETA Engine � ������� ������ ���� ETA
- WP-20: Shipping Engine � ������� ������ ���� �����
- WP-21: ����� ������ �������� ��������

## ������� 2: ������ ������ (��� ���� ������� 1.5)
- WP-30B: Session Management + Mission Lifecycle � ? �����
- WP-30C: Task Planner + Execution Engine � ? �����
- WP-30D: Decision Engine � ? �����
- WP-30E: Tool Implementations � ? �����
- WP-30F: Company Knowledge Layer Interface � ? �����
- WP-30G: Memory Interface Definition � ? �����
- WP-30H: Avatar Contract � ? �����
- WP-30I: Advanced Features � ? �����
- WP-31: AI Memory � ����� ������
- WP-32: Knowledge Graph � ��� ����� �������
- WP-33: Trade Intelligence � ���� ����� ��������� �������� � ? �����

## ������� 3: ����� ��������
- WP-40: ������ ������� �� Docker Compose
- WP-41: ����� ������� ������
- WP-42: ���� ������

---

# 8. ������ ������� �������

## 8.1 Work Packages ��������

| Work Package | ������ | ������� |
|--------------|--------|---------|
| WP-01 | ? ����� | ������� ����� Backend |
| WP-02A�H | ? ����� | ����� ���� ����� �������� |
| WP-03 | ? ����� | ����� ����� ���� �������� |
| WP-04 | ? ����� | ������ �� ����� CRUD |
| WP-05 | ? ����� | ������� ���� ������� |
| WP-06 | ? ����� | �������� ������� (21 ������) |
| WP-07 | ? ����� | ����� ������ |
| WP-08 | ? ����� | ����� ������ |
| WP-09 | ? ����� | ����� ����� ����� |
| WP-10 | ? ����� | ���� ����� Alembic |
| WP-11 | ? ����� | ����� ������� |
| WP-12 | ? ����� | Docker hardening |
| WP-13A | ? ����� | ���� �������� �������� |
| WP-15 | ? ����� | ������� ���� ���� �������� |
| WP-16B | ? ����� | ���� ������� �������� |
| WP-17A | ? ����� | �������� ���� ������� |
| WP-17B | ? ����� | �������� ���� ������� |
| WP-18 | ? ����� | ������� ������� ������ |
| WP-30B | ? ����� | Session Management + Mission Lifecycle |
| WP-30C | ? ����� | Task Planner + Execution Engine |
| WP-30D | ? ����� | Decision Engine |
| WP-30E | ? ����� | Tool Implementations |
| WP-30F | ? ����� | Company Knowledge Layer interface; KnowledgeProvider, KnowledgeQuery, KnowledgeProviderRegistry, ingestion contract |
| WP-30G | ? ����� | Memory Interface Definition; MemoryProvider ABC with recall/store/forget/summarize; graceful degradation in DEM core |
| WP-30H | ? ����� | Avatar Contract; IntentContent and AvatarRenderer interfaces defined; structured intents confirmed; 15 tests |

## 8.2 ������ �������� �������

- **Backend:** ���� ����� �� init_db()
- **Database:** SQLite �� schema ���� ������� ������
- **Frontend:** ���� �����
- **Tests:** 267 ������ pytest (259 ����ɡ 8 ������ ���� �������)
- **Routers:** �� 7 routers thin (�� ���� ����� �� SQL)
- **Service layer:** ���� ������� ����� ��������
- **Docker:** Dockerfiles � docker-compose ������

## 8.3 Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables via raw SQL if absent, applies incremental `_ensure_*_schema()` column additions, and inserts seed data
3. Alembic runs afterward for destructive cleanup migrations (`legacy_cleanup`, `invoices` rebuild)

## 8.4 Known Issues

- Frontend lint warnings exist in shadcn/ui generated components (not project-specific)
- `__pycache__` directories remain scattered throughout Python tree (mostly gitignored)

---

# 9. Architecture Principles

## 9.1 Mission

Nile Key is developed as a production-grade software platform.

Every engineering decision must improve:
* Stability
* Correctness
* Maintainability
* Scalability
* Security
* Readability

Speed is never more important than correctness.

## 9.2 Repository Ownership

Treat this repository as a long-term production system.

Every file belongs to the architecture.

Every dependency must have a purpose.

Every module must have an owner.

No code is "temporary."

## 9.3 Source of Truth

The single authoritative source of truth is:

**Backend Domain Models + Pydantic Schemas + OpenAPI Contract**

Everything else must conform to this.

Priority order:

1. Backend Pydantic Schemas
2. FastAPI API Contract
3. Business Rules
4. Database Schema
5. Frontend Types
6. Documentation

Never reverse this order.

## 9.4 Architecture Philosophy

Always prefer:

Refactor > Rewrite

Simplify > Expand

Reuse > Duplicate

Remove > Add

Consistency > Cleverness

Correctness > Speed

Long-term maintainability > Short-term convenience

## 9.5 Working Model

Before changing any code:

Understand.

Investigate.

Map dependencies.

Estimate impact.

Only then modify.

Never begin coding immediately after reading a request.

## 9.6 Repository Exploration Rules

Before significant modifications:

* inspect the complete project
* inspect dependencies
* inspect imports
* inspect architecture
* inspect configuration
* inspect build process
* inspect deployment
* inspect security
* inspect API contracts
* inspect database model

Never assume.

Always verify.

## 9.7 Modification Policy

Every modification must answer:

Why does this problem exist?

What breaks if ignored?

Risk level?

Files affected?

Expected benefit?

Rollback strategy?

## 9.8 Coding Principles

Never duplicate logic.

Never create dead code.

Never introduce hidden side effects.

Prefer explicit behavior.

Prefer small functions.

Prefer isolated modules.

Prefer deterministic behavior.

## 9.9 Database Rules

Database follows Backend.

Backend never follows Database.

SQLite schema is an implementation detail.

Business model lives in Backend Schemas.

Migrations become the only legal way to evolve persistence after Phase 3.

## 9.10 API Rules

FastAPI is the public contract.

Routers must reflect business operations.

Responses must remain consistent.

Validation belongs in Pydantic.

Business logic does not belong inside routers.

## 9.11 Frontend Rules

Frontend consumes the API.

Frontend never defines business rules.

Frontend types should eventually be generated from OpenAPI.

Avoid duplicated interfaces.

Never silently ignore API errors.

## 9.12 Security Rules

Never hardcode secrets.

Never trust client input.

Validate every request.

Hash passwords using approved algorithms.

Avoid wildcard CORS in production.

Follow least-privilege principles.

## 9.13 Performance Rules

Optimize only after correctness.

Avoid premature optimization.

Measure before changing.

Prefer simple solutions.

## 9.14 Documentation Rules

Documentation must describe reality.

Never document features that do not exist.

Whenever architecture changes:

Update documentation.

## 9.15 Architectural North Star

Nile Key must evolve toward:

Clean Architecture

Domain-driven organization

Well-defined API contracts

Reliable deployment

Comprehensive testing

Production readiness

without sacrificing simplicity.

---

# 10. Project Governance

## 10.1 Development Rules

1. �� ����� MUST ����� �� Master Roadmap v2.1 �����.
2. �� ����� MUST ��� �� Quality Gates.
3. �� ����� ���� ��� ���� ��������� ��������.
4. �� ����� ���� �������.
5. �� ��� ���� (temporary code).

## 10.2 Coding Standards

- Python: PEP 8
- TypeScript: ESLint + Prettier
- FastAPI: Pydantic schemas ������
- ����������: pytest ��� backend� Jest ��� frontend
- �������: docstrings ������ JSDoc ��� frontend

## 10.3 Review Rules

1. �� PR MUST ��� ������� �������.
2. �� PR MUST ���� �� ��� �� ����������.
3. �� PR MUST �� ���� ������.
4. �� PR MUST ����� ��� �������.

## 10.4 Testing Rules

1. �� ���� MUST ��� unit tests.
2. �� router MUST ��� integration tests.
3. ����� ���������� MUST ���� �� �� WP.
4. �� ��� ���� �������� ����.

## 10.5 Commit Policy

1. commit ���� ��� ����� ������.
2. ����� commit �����.
3. �� mixed-purpose commits.
4. �� commits ���� ������.

## 10.6 Branch Policy

- Branch naming: `type/description` (e.g., `feature/eta-engine`, `fix/shipping-rates`)
- Main branch: `main` (protected)
- Development branch: `develop` (protected)
- No direct commits to protected branches
- All changes via Pull Request
- PR requires at least one approval

## 10.7 Release Policy

- Versioning: Semantic Versioning (SemVer) � MAJOR.MINOR.PATCH
- Changelog: Maintained in `CHANGELOG.md`
- Release checklist:
  - [ ] All tests pass
  - [ ] Docker build succeeds
  - [ ] Frontend build succeeds
  - [ ] Documentation updated
  - [ ] No critical TECH_DEBT.md items introduced
  - [ ] Phase exit criteria met (if applicable)

## 10.8 Quality Gates

��� ������ �� WP ������:

- [ ] ������� ����
- [ ] Backend ����
- [ ] Frontend ����
- [ ] �������� �������� ����
- [ ] �������� ����
- [ ] �� ��������� ������
- [ ] �� ������ ������
- [ ] �� ����� ��� ����� ����
- [ ] ���������� ����

## 10.9 Risk Management

| �������� | �������� | ������� | ��������� |
|---------|---------|---------|----------|
| ����� ETA Schema | ���� | ���� | ����� ��� ����� ����� |
| ���� ETA API | ����� | ���� | ���� ����� ��� API |
| ����� Shipping Providers | ����� | ����� | Registry pattern |
| ����� ����� ������ | ����� | ����� | WP dedicated ������� |
| ��� ������� | ����� | ����� | Phase prioritization |

## 10.10 Technical Debt Policy

- �� ��� ���� MUST ����� �� TECH_DEBT.md.
- �� ��� ���� MUST �� ��� ����.
- �� ��� ���� ���� ���� ��� ����.
- ������ ����� ������ �� WP.

## 10.11 Architecture Preservation Policy

- ������ ��� �������.
- ������ ��� ������.
- ������ ��� ������.
- �� ����� ������ ���� ����� �� Architectural Decision Log.

---

# 11. Execution Charter

## 11.1 �����

��� ����� ���� ��� ��� ��� ANY Digital Export Manager �� ����� ����� ����� ��� ��� ��������.

## 11.2 ������� ���������

1. **Never skip phases.** �� ����� ��� ������� ����.
2. **Never ignore dependencies.** ���� �� ��������� ��� �����.
3. **Always investigate before modifying.** ���á ��ѡ ���ޡ THEN ����.
4. **Always verify before closing.** ����� �� ��� ��� ����� �������.
5. **Always follow project gates.** �� ����� Gate checks.
6. **Always preserve architecture.** �������� ��� ������ �����.
7. **Always preserve business vision.** ������ ������� �� ���.
8. **Never create duplicate implementations.** �� �����.
9. **Never bypass testing.** ���������� �������.
10. **Always document major decisions.** �� ���� ��� ����� ���.
11. **Always keep repository consistent.** ������� ������� ������.
12. **Always respect roadmap order.** �� ���� ���� �������.
13. **Always continue from the latest completed work package.** ���� �� ��� ����� �������.
14. **Always update CURRENT_STATUS.md ��� �� ����� WP.**
15. **Always update TECH_DEBT.md ��� ������ ��� ����.**
16. **Always update ��� ������� ��� ����� ������� ���������.**
17. **Always read TECH_DEBT.md ��� ��� �� WP.** ���� �� �� ������ �������� �� ����.
18. **Always check git history ��� ����� ��� �����.** ���� ������ ��� �������.

## 11.3 ����� �����

```
��� �� �����:
1. ���� ��� ������� ������.
2. ���� CURRENT_STATUS.md.
3. ���� TECH_DEBT.md.
4. ��� WP �������.
5. ��� ��������� ��������.
6. ���� �� �� ��������� ������.
7. ���� git history ������� �������.
8. THEN ���� �����.
```

---

# 12. Project Continuity Protocol

## 12.1 �����

���� ��������� ������� ��� �� ����� ������� ������ ������.

��� ���������� ���� �����:
- **Self-healing:** ������� ���� ���� ����� �������� �� �������.
- **Crash-resistant:** �� ���� AI �� ����� ����� ��������� �� ��� ���� ����.
- **Multi-session:** ���� ������ ����� ��� ����� ChatGPT/Kilo ������.
- **Long-duration:** ���� ��� ������ ���� ���� ����� ������.

## 12.2 ����� �����������

### 12.2.1 ������� ��� ������ ������ (�� ���)

1. ���� Master Roadmap v2.1 (��� �����) ������.
2. ���� CURRENT_STATUS.md.
3. ���� TECH_DEBT.md.
4. ��� ������� ������� �� ����� 12.3.
5. ��� Work Package �������.
6. ��� ������ ��������.
7. ��� ������ ��������.
8. ��� ������ ������� �������.
9. ���� �� �� ��������� �������� ������ (��� Quality Gates).
10. ������ ����� �� ������ �������.

### 12.2.2 ������� ��� ������ ���� AI (ChatGPT/Kilo)

1. ��� AI ���� CURRENT_STATUS.md ��� ������ ������.
2. ��� AI ���� Master Roadmap v2.1 (��� 12.3 � ����� �����������).
3. ������ ������� ���� �� LAST_UPDATE �� CURRENT_STATUS.md.
4. �� ����� ������ ������� ������ ����� ���������.
5. ��� ����� ������ ���� (���� �����):
   - ���� �� ��� committed changes �� Git.
   - ���� CURRENT_STATUS.md.
   - ������ �� ��� WP ������ �����.

### 12.2.3 ������� ��� ������ ������ �� Crash

1. ��� ����� ����� ������:
   - ���� �� �� ������� ������ �� `.env.example` �� ���� �����.
   - ���� �� �� Dependencies �� `requirements.txt` � `package.json` �� �����.
   - ���� �� �� Docker images �������� �� ���� ������.
2. ���� Master Roadmap v2.1 (��� �����).
3. ���� CURRENT_STATUS.md.
4. ���� git log ���� commits.
5. ��� ��� ���� ���� ������ �� ��������� �������� (ETA API, Shipping APIs).
6. ��� CURRENT_STATUS.md ������ ���������.
7. ������ �� ��� WP ������.

### 12.2.4 ������� ��� ������ ���� ����

1. ���� README.md.
2. ���� Master Roadmap v2.1 (��� �����).
3. ���� PLAN.md Sections 9�10 (���� ��� � �� ��� ����� ARCHITECTURE_CHARTER.md ���).
4. ���� CURRENT_STATUS.md.
5. ���� TECH_DEBT.md.
6. ���� ����� ����������� (12.2.1).

### 12.2.5 ������� ��� ���� ������� ���� ����

1. ���� Master Roadmap v2.1 ������.
2. ���� CURRENT_STATUS.md.
3. ���� git log ���� commits.
4. ���� �� �� ������ �� ���� ����� (Python version, dependencies).
5. ��� ��� ���� ���� ������ �� ��������� �������� (ETA API, Shipping APIs).
6. ��� CURRENT_STATUS.md ������ ���������.
7. ������ �� ��� WP ������.

### 12.2.6 ���� Handoff ��� �������

�� ���� AI MUST ����:
1. **Checkpoint:** ��� �� CURRENT_STATUS.md �����:
   - �������
   - ��� WP ��������
   - ������� �������
   - ���������� �������
   - ������� ��������
   - ������ �������
2. **State Snapshot:** ��� ����� ������ �������.
3. **Next Action:** ������ ������� ������� ���� ����.

### 12.2.7 ����� �� ����� ������

- **No orphaned work:** �� ���� WP ����� ���� ����� WP �������.
- **No silent failures:** ��� ��� �����ѡ ��� ����� �� TECH_DEBT.md.
- **No undocumented changes:** �� ����� MUST ����� �� Master Roadmap v2.1 �����.
- **Atomic commits:** �� commit �� ��� ���� ����.
- **Branch per WP:** �� WP ���� ��� ��� ����� ���� ��� ������.

## 12.3 ����� ����������� (���������)

?? **��� ������� MUST ����� ��� �� ����� WP.**

| ����� | ������ ������� |
|------|---------------|
| ��� ����� | 2026-07-29 |
| ������� ������� | 3 � ����� �������� |
| Work Package الحالية | WP-42 (DEFERRED — OPEN) |
| ������� ������� | ����� |
| WP ������� ������� | Release Readiness Closure |
| المهام المكتملة | WP-01 through WP-41 |
| المهام المتبقية | WP-42 Owner Acceptance + Release validation |
| ������� �������� | ��� ���� ����� ����� �� ETA � Shipping APIs |
| ������� ��������� | ����� Master Roadmap v2.1 + CURRENT_STATUS.md + TECH_DEBT.md |
| Branch ������ | main |
| Commit ������ | feat(ov-001): close Stage 6 UX verification and evidence |

## 12.4 Session Recovery Rules

1. **Checkpoint format:** ��� �� WP� ��� �� CURRENT_STATUS.md:
   - �������
   - ��� WP ��������
   - ������� �������
   - ���������� �������
   - ������� ��������
   - ������ �������

2. **Resumability:** �� ���� ����� ������ �� ���� �� CURRENT_STATUS.md ��� Reading ����� ���������.

3. **State hydration:** ��� ���� ������� ����� �� ����ڡ ����:
   - ������� ������ �� `.env.example`
   - Dependencies �� `requirements.txt`
   - Versions �� `package.json`
   - Docker images ��������
   - External API requirements (ETA, Shipping providers)

4. **Crash recovery order:**
   1. ���� �� ����� ������� (git status).
   2. ���� CURRENT_STATUS.md.
   3. ���� Master Roadmap v2.1 ��� 12.3.
   4. ��� ��� WP ������.
   5. ������ �� ����.

5. **Power failure protocol:**
   - ��� ��� �� WP: ���� �� �� `.env` ����� �����.
   - ��� ������� ������: ���� �� �� `init_db()` ����.
   - ��� ������� ������: ���� �� �� ���������� ����.

6. **Developer change protocol:**
   - ������ ������ MUST ���� Master Roadmap v2.1 �������.
   - ������ ������ MUST ���� CURRENT_STATUS.md.
   - ������ ������ MUST ���� TECH_DEBT.md.
   - ������ ������ MUST ���� Section 12.2.4.

---


# 13. Architectural Decision Log

## 13.1 �����

����� �� ���� ������ ��� �� ������ �������.

## 13.2 ��� ��������

| ������ | ����� | ������ | ������� | ��������� | ������� ������� | ���� �������� |
|--------|-------|--------|---------|-----------|---------------|---------------|
| FastAPI + React + SQLite | ����ɡ �����ɡ ������ ����� | WP-01 ����� | Django, Flask, Frappe | ���� vs ����� | ���� MVP ���� ������ | ��� ������ �� PostgreSQL |
| ���� ����� ������ | ��� ���������� | WP-15, WP-16B | ���� �� routers | ����� vs ������ ������� | �������� ���� ���� ���� | ��� ����� ���� ���� |
| Pydantic ������ | ���� ������ ����� API | WP-02A�H | Marshmallow, ���� | ����� vs ���� | API ����� | ��� ����� ���� �������� |
| JWT + bcrypt | ����� ��� ������ | WP-03 | sessions, OAuth2 | ����� vs ����� | ������ ������ | ��� ������ �� SSO |
| Raw SQL �� SQLite | ���� ���� �� ORM | WP-09, WP-10 | SQLAlchemy | ����� vs ������� | ����� ������� | ��� �������� �� PostgreSQL |
| ���� ETA ������ | ��� ���������� | WP-19 ����� | ��� �� invoice service | ����� vs ����� | ������ ������ | ��� ����� fields ����� |
| ���� Shipping ������ | ��� ���������� | WP-20 ����� | ��� �� shipment service | ����� vs ����� | ������ ������ | ��� ����� provider ���� |
| Phase 1.5 ������� | ������� ���� ������� ��� ������ | Forensic Analysis | ���� ������� ������ �� AI | ��� vs ���� | ���� ������ �� ����� ��� | ��� ��� Phase 1.5 |
| SQLite ������� MVP | �� ������ �����ɡ ���� ����� | forensic analysis | PostgreSQL ������ | ���� vs ����� | MVP ���� ������� ����� | ��� ������ ����� ������ |
| ����� PostgreSQL | ������ ����� ������� ����� | forensic analysis | PostgreSQL �� ������� | ����� vs ���� | Docker migration path ���� | ��� ������ �� production database |
| httpx ����� �� requests | ������ �� asyncio� FastAPI | WP-19 | requests | ���� vs ����� | ���� HTTP ���� | ��� ����� ����� HTTP |
| OAuth2 client_credentials | ������ �� ETA API | forensic analysis | API Key, Basic Auth | ���� vs ����� | ����� ����� �� ETA | ��� ����� ETA auth model |
| ����� ETA ������ | ��� ������ ������� �� ����� �������� | WP-19 | ��� �� invoices | ����� vs ����� | ���� ���� ������� ETA | ��� ��� ������� |
| Pydantic schemas ������ �� ETA v1.0/v1.2 | ����� �� ������� ETA ������� | forensic analysis | schemas ����� | ����� vs ����� | ���� �� ETA | ��� ����� ������� ETA |
| Browser Automation Platform � two-document structure | ����� ����� ���� ����� �����ɺ ������� ������� ����� �� Architecture | BA-DEC-001 | Single document or three-way split | ����� ����� ����� ������� | ���� ����� ������ ������ ������� | ��� ����� ���� Browser Automation ����� |
| Browser Automation Platform � in-repo isolated subtree | ������ ��� ���� Browser Automation ����� ��� ������ ���� ����� ������� | BA-ARCH-001 Section 2� .playwright-mcp/ evidence | Runtime integration �� separate repository | ����� ����� ������ | ���� �����ɡ ��� Docker ������� ���� ����� | ��� ����� ���� Docker |
| Browser Automation � Chromium only for initial release | ����� flakiness ������ ��� ������� | ADR-BA-002 | Support all three browsers (Chromium + Firefox + WebKit) | ����� ����� ������� | ��� flakiness� ���� ����� | ��� ������� ������ |
| Browser Automation � MCP as enhancement, not requirement | ������� ��� �� ���� ���� MCP | ADR-BA-003� .playwright-mcp/ empty directory | Make MCP required for all test execution | ����� ���� ������� ����� ����� | ���� ���� ������ MCP ���� ��� | ��� ���� @playwright/mcp |
| Browser Automation Platform � Phase 0 approval | Project Owner approval of BA-ARCH-001 and BA-IMPL-001 per BA-DEC-001 | PO-BA-2026-001 | Defer or reject | approval vs delay | Phase 0 closed; Phase 1 authorized | Upon signature |
| Browser Automation Platform � scope freeze | No changes to architecture or implementation scope without formal change request | BA-WP-001 Phase 0 Task 0.3 | Uncontrolled changes | freeze vs flexibility | Scope stable for execution | Upon change request |

---

# 14. Implementation Rules

## 14.1 ��� ����� ������� MUST ����:

### 14.1.1 �����
����� ��� ������� ����ȿ �� ������� ���� ����ǿ

### 14.1.2 ��������� ��������
�� �� ��� Prerequisites� �� �� �����ɿ

### 14.1.3 ��������
�� �� �������� �������ɿ (API keys, ������, ���)

### 14.1.4 ��������
�� �� �������� �������ɿ (�����, �����, APIs)

### 14.1.5 ����� �������
�� �� ����� ������� ������� ������ǿ

### 14.1.6 ������ ������
��� ���� �� ������� ��Ϳ

### 14.1.7 ��� �������
���� ���� ��� ��� ������п ��� ���� ����ݿ

### 14.1.8 ����� ������
��� ����� �� ��� ������п

### 14.1.9 �������� ��������
�� �� ���������� �������� ���� ��� ������� �������ɿ

### 14.1.10 ������ �������
�� ������ ���� ������� ��� ��� ������п

---

# 15. Work Packages

## 15.1 ������� 1: ������ ?

### WP-01: ���� ������� ����� FastAPI
- ? �����

### WP-02A�H: ����� ���� ����� ��������
- ? �����

### WP-03: ����� ����� ���� ��������
- ? �����

### WP-04: ������ �� ����� CRUD
- ? �����

### WP-05: ������� ���� �������
- ? �����

### WP-06: �������� �������
- ? ����� (21 ������)

### WP-07: ����� ������
- ? ����� (SECRET_KEY, CORS)

### WP-08: ����� ������
- ? ����� (.env, execute_update)

### WP-09: ����� ����� �����
- ? �����

### WP-10: ���� ����� Alembic
- ? �����

### WP-11: ����� �������
- ? �����

### WP-12: Docker hardening
- ? �����

### WP-13A: ���� �������� ��������
- ? �����

### WP-15: ���� ���� ��������
- ? �����

### WP-16B: ���� ������� ��������
- ? �����

### WP-17A: �������� ���� �������
- ? ����� (48 ������ ����)

### WP-17B: �������� ���� �������
- ? ����� (59 ������ ����)

### WP-18: ������� ������� ������
- ? �����

## 15.2 ������� 1.5: ����� ������ ���� ������� (������)

### WP-19: ETA Engine
- �����: ������� ���� ������� �������� �� ������ `erpnext_egypt_compliance`
- ������: ? �����
- ��������� ��������: Phase 1 ������
- ��������: ���� ETA ����� + ����� ������ + �������� 50+
- ������ ������:
  - [x] ����� Pydantic �������� ����������� ������ �� ETA Schema v1.0
  - [x] ����� Pydantic ������� ���������� ������ �� ETA Receipt Schema v1.2
  - [x] ����� OAuth2 �� ����� Preprod � Production
  - [x] ����� ������ ������� ��� Preprod ������� ��� UUID (���ҡ ����� API keys)
  - [x] ��� ���� �������� ��������
  - [x] ���� Pydantic ���� ����� ������ ��� ������
  - [x] ����� ����� ������� ���� �� ���� (APScheduler)
  - [ ] ������� ������ ���������� ����� ��� ������ (���� ��� WP-21)
  - [x] �������� ����: 71 ������ ����
- ���������� �������: ������ ��� ����� ������ �� `invoices` service ����� �������

### WP-20: Shipping Engine
- �����: ������� ���� ������� �������� �� ������ `erpnext-shipping`
- ������: ?? �����
- ��������� ��������: Phase 1 ������
- ��������: ����� ����� + ����� API + �������� 40+
- ������ ������:
  - [x] LetMeShip: ���� ����ѡ ����� ���ɡ ���ޡ ����
  - [x] SendCloud: ���� ����ѡ ����� ���ɡ ���ޡ ���ڡ �����
  - [x] ���� ����� ������ ����
  - [x] ���� �������� ����� ������� ����
  - [x] ������ ������� ���� ����� �����
  - [x] ����� �������� ����� ������
  - [x] �������� ����: 40+ ������ ����
- ���������� �������: ����� `get_rates()` ������ ���� �������

### WP-21: ����� ������ �������� ��������
- �����: ��� ETA Engine � Shipping Engine �� ���� ���� Nile Key
- ������: ? �����
- ��������� ��������: WP-19 + WP-20 ��������
- ������ ������:
  - [x] ���� �������� ����� ������ �����
  - [x] ���� ������� ���� ������ ��� �� ETA ������
  - [x] ��� ������� ���� ����� ��������
  - [x] ��������� ���� ��� ������ ����������
  - [x] ����� ���� ��� ���� ��������

## 15.3 ������� 2: ������ ������

### WP-30: Digital Export Manager
- ? �����

### WP-31: AI Memory
- **Status:** ✅ Completed
- **Description:** Long-Term Memory layer implemented via SQLiteMemoryProvider with MemoryProvider interface
- **Dependencies:** WP-30F, WP-30G, WP-30I completed
- **Deliverables:** MemoryProvider interface, SQLite persistence, graceful degradation, 13 tests
- **Completion Date:** 2026-07-26

### WP-LLM-001: LLM Provider Integration
- **Status:** ✅ Completed
- **Description:** Google AI (Gemini) provider integrated via `backend/app/agent/llm/provider.py`; DEM reasoning enhanced with LLM candidate selection and reasoning text improvement; graceful degradation when LLM unavailable
- **Dependencies:** WP-30 (DEM Core), WP-30F, WP-30G completed
- **Deliverables:** GeminiProvider implementation, LLM registry integration, DEM-LLM reasoning enhancement, 24 tests (12 unit + 6 integration + 6 performance)
- **Completion Date:** 2026-08-07

### WP-32: Knowledge Graph
- �����: ��� ����� �������� �������� �� ������ ������ ������� ������� ��������
- ������: ? �����
- ��������� ��������: WP-30F, WP-30G ��������
- ��������: 9 ����� ��ϡ 9 ���� ����� API� ����� MemoryProvider� ����ޡ 105 ������
- ������ ������:
  - [x] 9 ����� ��� ������ (customer, supplier, shipment, invoice, document, resource, hs_code, customs_declaration, export_workflow)
  - [x] 9 ���� ����� API ����
  - [x] ������ ������� ������ �� ����� �������
  - [x] ������ ����� ������� ����
  - [x] ������ �������� ����
  - [x] ����� MemoryProvider �� graceful degradation
  - [x] ����� ������� ����� ��������
  - [x] 105 ������ ����

### WP-33: Trade Intelligence
- **Status:** ✅ Completed
- **Description:** Trade Intelligence — supplier/buyer analysis, trend detection, comparisons, report generation
- **Dependencies:** WP-30F, WP-30G, WP-31, WP-32 completed
- **Deliverables:** Intelligence engine, 6 API endpoints, 120 tests (75 service + 26 integration + 14 security + 5 performance)
- **Completion Date:** 2026-08-09

### WP-34: External Research Capability
- **Status:** ✅ Completed
- **Description:** External Research lifecycle with full traceability
- **Dependencies:** WP-30F, WP-30G, WP-30H, WP-31, WP-32, WP-33
- **Deliverables:** Research Request/Result models, orchestrator, source registry, retrieval abstraction, evidence/provenance capture, result structuring, verification/quality, 103+ tests
- **Completion Date:** 2026-08-09

## 15.4 ������� 3: ����� ��������

### WP-40: ������ ������� �� Docker Compose
- ? �����

### WP-41: ����� ������� ������
- ? �����

### WP-42: ���� ������
- ? �����

---

# 16. Phase Exit Criteria

## 16.1 ������� 1: ������

? ������ ���:
- [ ] ���� WP-01 through WP-18 ������
- [ ] 176+ ������ ����
- [ ] Backend ���� ���� �����
- [ ] Frontend ���� �����
- [ ] Docker artifacts ������

## 16.2 ������� 1.5: ����� ������ ���� �������

? ������ ���:
- [x] WP-19: ETA Engine ���� �������
  - [x] ����� OAuth2 �� Preprod � Production
  - [x] ����� ������ ������ ��� Preprod ������� ��� UUID (���ҡ ����� API keys)
  - [x] ����� ����� ������� ���� (APScheduler)
  - [ ] ������� ������ ���������� ����� (���� ��� WP-21)
  - [x] 50+ ������ ���� ���� (71 ������)
- [x] WP-20: Shipping Engine ���� �������
  - [x] LetMeShip API ������ (����ѡ ������ ���ޡ ����)
  - [x] SendCloud API ������ (����ѡ ������ ���ޡ ���ڡ �����)
  - [x] ���� ������ ��������� ����
  - [x] 40+ ������ ���� ����
- [x] WP-21: ����� ������ �������� �������� �����
  - [x] ���� �������� �����
  - [x] ���� ������� ���� ������ ���
  - [x] ��� ������� ����
  - [x] ��������� ����
- [ ] �� ���� mock data �� �������� ������
- [ ] ���� ���������� ������� �� ���� ����
- [ ] ������� ����

## 16.3 ������� 2: ������ ������

? ������ ���:
- [x] ���� WP-30 through WP-33 ������
- [ ] Digital Export Manager ������ ���������� �������
- [ ] AI Memory ���� Across �������
- [ ] Knowledge Graph ���� ������ ��������
- [x] Trade Intelligence ���� ������
- [x] 100+ ������ ���� ����

## 16.4 ������� 3: ����� ��������

? ������ ���:
- [x] WP-40: Docker Compose ���� �� �������
- [x] WP-41: ����� ������� ������
- [ ] WP-42: قبول المالك (DEFERRED — OPEN)
- [ ] �� ���� ��� ���� ���� ���� �������
- [ ] ���� ���������� ����
- [ ] �������� ���������� �����

---

# 17. Traceability Matrix

## 17.1 Business Goal ? Capability ? WP ? Implementation

| Business Goal | Capability | WP | Implementation | Testing | Production |
|---------------|-----------|-----|----------------|---------|------------|
| ������ ����� ���� | ETA Compliance | WP-19 | ETA Engine package | 50+ tests | WP-40 |
| ����� ����� | Shipping Management | WP-20 | Shipping Engine package | 40+ tests | WP-40 |
| ����� ����� | Customs Clearance | WP-01�18 | Customs Engine | ? Complete | ? Ready |
| ����� ������ | Supplier Management | WP-13A | Suppliers Service | ? Complete | ? Ready |
| ����� ����� | Customer Management | WP-13A | Customers Service | ? Complete | ? Ready |
| ����� ������ | Invoice Management | WP-19 | ETA Engine | 50+ tests | WP-40 |
| ����� ����� | Document Management | WP-15 | Documents Service | ? Complete | ? Ready |
| ������ ����� | Export Operations | WP-21 | Integration | WP-21 tests | WP-40 |
| ���� ����� | Trade Intelligence | WP-33 | Intelligence Engine | WP-33 tests | WP-42 |
| ��� ����� | Knowledge Graph | WP-32 | Knowledge Graph | WP-32 tests | WP-42 |
| ���� ��� | Digital Export Manager | WP-30 | Digital Export Manager | WP-30 tests | WP-42 |
| ����� ���� | Administration | WP-01�18 | Auth + Core | ? Complete | ? Ready |
| ������ ����� ����� | Reports & Dashboard | WP-21 | Dashboard Integration | WP-21 tests | WP-40 |
| ��� ����� | Audit & Compliance | WP-21 | Audit Logs | WP-21 tests | WP-40 |
| ������� | Notifications | WP-19, WP-20 | Notification Service | WP-19/20 tests | WP-40 |

---

# 18. Git Policies

## 18.1 Branch Naming

- `main` � production-ready code
- `develop` � integration branch
- `feature/{wp-number}-{description}` � new features (e.g., `feature/wp19-eta-engine`)
- `fix/{description}` � bug fixes
- `hotfix/{description}` � production hotfixes
- `chore/{description}` � maintenance tasks

## 18.2 Branch Protection

- `main` and `develop` are protected branches
- No direct commits to protected branches
- All changes via Pull Request
- PR requires at least one approval
- CI must pass before merge

## 18.3 Versioning Strategy

- Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes
- Phase milestones: v1.0.0 (Phase 1), v1.5.0 (Phase 1.5), v2.0.0 (Phase 2), v3.0.0 (Phase 3)

## 18.4 Release Checklist

- [ ] All tests pass
- [ ] Docker build succeeds
- [ ] Frontend build succeeds
- [ ] Documentation updated
- [ ] No critical TECH_DEBT.md items introduced
- [ ] Phase exit criteria met
- [ ] CHANGELOG.md updated
- [ ] Version bumped in relevant files

---

# 19. Technical Debt Register

## 19.1 Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| HIGH | Documentation drift | Multiple docs | Resolved in WP-17A/WP-17B |
| MEDIUM | Raw SQL everywhere | `database.py`, all routers | No ORM abstraction; schema changes require coordinated manual updates |
| MEDIUM | Docker deployment unverified | Dockerfiles, `docker-compose.yml` | RESOLVED � Both images build successfully; `docker compose up --build` verified with healthy services; database persistence confirmed via Docker volume |
| MEDIUM | No rate limiting | Missing entirely | Listed in this document as required but not implemented |
| MEDIUM | PostgreSQL migration path | Not started | This document notes SQLite is an implementation detail |
| LOW | Root `alembic.ini` exists | Project root | Real config is `backend/alembic.ini`; root copy is stale/untracked |
| LOW | `__pycache__` directories | Throughout Python tree | Mostly gitignored, but scattered `__pycache__` dirs remain |

## 19.2 Resolved Technical Debt

| Debt | Resolution | Work Package |
|------|------------|--------------|
| Schema-database mismatch | `_create_tables()` and `_ensure_*_schema()` aligned | WP-02A�H |
| Hardcoded SECRET_KEY | Externalized to environment; fails fast when missing | WP-07 |
| Wildcard CORS default | Reads from `ALLOWED_ORIGINS` | WP-07 |
| Code duplication in UPDATE helpers | `execute_update()` extracted and integrated into 8 routers | WP-09 |
| Legacy column filtering in routers | Compatibility shims removed; response mapping simplified | WP-09, post-WP-10 |
| Missing Alembic migration system | Alembic initialized; migration chain present | WP-10 |
| Legacy `invoices.uuid` column | SQLite-safe table rebuild migration removes it | WP-10 |
| `.env.example` drift | Aligned with `config.py` variables and formats | WP-08 |
| Empty services layer | Service modules implemented for all 7 non-auth domains with shared base infrastructure | WP-15, WP-16B |
| Business logic in routers | Migrated to service layer; routers now thin | WP-13A, WP-15 |
| Manual frontend types | Generated types via `openapi-typescript`; verified to match API | WP-12 |
| Customs HS-code created_at mismatch | Added `created_at` to `_ensure_hs_codes_schema()` with backfill | WP-18 |
| Document upload type omission | Fixed `upload_document()` INSERT to populate required `type` column | WP-18 |
| Docker deployment validation | Docker artifacts reviewed and validated against project configuration | WP-18 |

---

# 20. Cross-References

## 20.1 ������� ��������

| ������� | ������� ���� ������� |
|---------|---------------------|
| ARCHITECTURE_CHARTER.md | **�������** � �� ��� ������ �� ��� ������� (������� 9 � 10). ����� �� `.kilo/plans/archive/`. |
| CURRENT_STATUS.md | ����� ����� � ����� ��� �� WP. ����� �� ��� ������� ���� ������ �������. |
| TECH_DEBT.md | ����� ����� � ����� ��� ������ ��� ����. ����� �� ��� ������� ��� ��� �� WP. |
| README.md | ����� ���� � ������ �� ��� �������. �� ����� ��� ������ �������. |
| DEPLOYMENT.md | **���� �� ����� 24.** ����� �� `.kilo/plans/archive/`. |
| CHANGELOG.md | ����� ����� � ����� �� �� �����. |
| PROJECT_EXECUTION_RULES.md | **���� �� ����� 23.** ����� �� `.kilo/plans/archive/`. |
| WORK_PACKAGE_PLAN.md | **���� ����** �� `.kilo/plans/archive/WORK_PACKAGE_PLAN.md`. |
| PROJECT_BASELINE.md | **���� �� ����� 22.** ����� �� `.kilo/plans/archive/`. |
| FINAL_BASELINE.md | **���� �� ����� 22.** ����� �� `.kilo/plans/archive/`. |
| BASELINE_SUMMARY.md | **���� �� ����� 22.** ����� �� `.kilo/plans/archive/`. |
| PROJECT_BASELINE_AFTER_WP21.md | **���� �� ����� 22.** ����� �� `.kilo/plans/archive/`. |
| REPOSITORY_INTELLIGENCE.md | **���� �� ����� 25.** ����� �� `.kilo/plans/archive/`. |
| ENGINEERING_MEMORY.md | ��� �������� �������� � �����. |
| ED-WP30-001 | ���� ����� � �����. |
| ED-WP30-002 | ���� ����� � �����. |
| ED-WP32-001 | ���� ����� � �����. |
| MEMORY_CONTRACT.md | ��� � �����. |
| KNOWLEDGE_INGESTION_CONTRACT.md | ��� � �����. |
| AVATAR_CONTRACT.md | ��� � �����. |
| UAT_CHECKLIST.md | ���� � `docs/appendices/UAT_CHECKLIST.md`. |
| docs/architecture/ADR-0001-shipments-legacy-columns.md | ���� ������ � �����. |

## 20.2 ���� ���������

```
PLAN.md (Master Roadmap v2.1) ? ������ ������
    ??? CURRENT_STATUS.md (���� ������� �������)
    ??? TECH_DEBT.md (��� ����� ������)
    ??? CHANGELOG.md (��� ���������)
    ??? docs/appendices/ (����� �������)
    ?   ??? .kilo/plans/archive/WORK_PACKAGE_PLAN.md — Historical detailed WP breakdowns
    ?   ??? UAT_CHECKLIST.md � Manual UAT checklist
    ?   ??? ...
    ??? .kilo/plans/earp-001/ (���� ����� EARP-001)
    ??? .kilo/plans/ED-*.md (������ ������)
    ??? .kilo/plans/*-spec.md (�������)
    ??? .kilo/plans/*-contract.md (����)
    ??? .kilo/plans/archive/ (����� ������� ���������)
```

## 20.3 ����� ��������

��� ����� �� ����� �� PLAN.md:
1. ������ PLAN.md ������ ������
2. ������� ������� �������� ������� PLAN.md
3. ��������� �������� �� `.kilo/plans/archive/` �� ���� ���� �������� ������ �������� ���
4. ��������� �������� (ED, EAD, ADR, ������) ���� ���� �� ������ ��� ��� ������ �� PLAN.md

---

# 21. Political Final Policy

��� ������� �� ������ ������ �������. �� ����� ����� ��� �����.

�� ���� ����� ���� �����.
�� ���� ���� ������ ���� ��� �������.
�� ���� ��� ����� ���� ��� ������.

�������� ��� ������ �����.
����� ������.
������� ������.

��� ����� ��� �� ��� ������ϡ
����� ����� ��� ����� ���.

---

# 22. Architecture Vision Statement

## 22.1 Target Architecture

Nile Key is an Intelligent Operating Platform, not a traditional ERP with AI features.

Digital Export Manager (DEM) is the first Executive Intelligence Layer in the platform.

Architecture layers:
- Executive Intelligence: DEM
- Cognitive: Reasoning Engine, Company Knowledge Layer, Long-Term Memory (WP-31)
- Planning: Task Planner, Execution Planner
- Orchestration: Tool Orchestrator
- Business / ERP Services: Shipping, ETA, Customs, Suppliers, Customers, Documents, Resources, Notifications, Audit, Workflow, Dashboard, Search
- Database: SQLite (MVP) → PostgreSQL (Production)

## 22.2 Current Implementation Status

Current intelligence implementation includes Deterministic/Scaffolded Intelligence — rule-based, interfaces, and registry-driven — plus an active LLM Provider integration (WP-LLM-001).

- **LLM Provider:** Google AI (Gemini) integrated via `backend/app/agent/llm/provider.py`
- **LLM Registry:** `llm_registry` singleton manages provider registration
- **DEM Integration:** `ReasoningEngine` uses `llm_registry` for candidate enhancement and reasoning improvement with graceful degradation
- **Config:** `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` in `backend/app/core/config.py`

Absence of a current LLM is not an architectural failure; it is an architecture-ready step toward a future target.

## 22.3 Deferred / Future

- Knowledge Ingestion Pipeline — contract defined, implementation deferred
- Avatar Renderer — contract defined, implementation deferred
- Goal and Plan reasoning layers — deferred to future work packages
- Multi-agent coordination — future
- Full export operations autonomy — future

---

## 22.1 Backend Status

- **Entry point:** `backend/main.py`
- **Config:** `SECRET_KEY` required from environment; validates 32+ char length
- **Database:** SQLite via raw `sqlite3` module; `init_db()` owns schema creation
- **Security:** JWT + bcrypt; CORS restricted to `ALLOWED_ORIGINS`; CSRF middleware active
- **Schedulers:** APScheduler for ETA (hourly) and Shipping (daily)
- **Import status:** All modules import cleanly
- **Startup blockers:** None detected

### Registered Routers (16 in main.py)

1. `auth.router` � Authentication & RBAC
2. `suppliers.router` � Supplier management
3. `customers.router` � Customer management + CSV import
4. `shipping.router` � Shipping rates, tracking, providers
5. `invoice.router` � Invoice management
6. `customs.router` � HS codes, duty calculation, declarations
7. `documents.router` � Document upload and management
8. `resources.router` � Guides and regulations
9. `eta.router` � Egyptian Tax Authority e-invoicing
10. `notifications.router` � Notification management
11. `audit.router` � Audit log queries
12. `workflow.router` � Export workflow lifecycle
13. `digital_export_manager_router` � DEM facade
14. `knowledge_graph.router` � Knowledge graph operations
15. `trade_intelligence.router` � Trade intelligence analysis
16. `dashboard.router` � Dashboard statistics

## 22.2 Frontend Status

- **Entry point:** `frontend/src/main.tsx`
- **Framework:** React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Build status:** `npm run build` passes
- **Pages:** 11 pages (Login, Dashboard, Suppliers, Customers, Shipments, Invoices, Customs, Documents, Resources, Notifications, Profile)
- **Test status:** Vitest tests pass for Notifications and NotificationBell

## 22.3 Database Status

- **Engine:** SQLite (`nile_key.db`)
- **Schema creation:** `init_db()` via raw SQL with `_ensure_*_schema()` column additions
- **Migrations:** Alembic chain: `9f6e6d58ca0f_initial` ? `0f82a20f2bb7_legacy_cleanup` ? `bdab744e83e3_legacy_cleanup_fix`
- **Tables:** 20+ tables including users, roles, suppliers, customers, shipments, invoices, customs_declarations, hs_codes, documents, resources, shipping_providers, shipping_parcel_templates, shipping_labels, shipping_logs, contacts, addresses, eta_connectors, eta_logs, eta_log_documents, knowledge_nodes, knowledge_edges, export_workflows, audit_logs, notification_templates, notification_logs, notification_preferences, agent_sessions, missions

## 22.4 Test Status

| Category | Count | Status |
|----------|-------|--------|
| Backend pytest tests | 876+ | ? Passing (5 pre-existing failures) |
| Backend skipped | 8 | ? By design |
| Frontend Vitest tests | 17 | ? Passing |
| Total test files | 56 backend + 2 frontend | ? All passing |
| Service-layer unit tests | 59 | ? Passing |
| Integration tests | 48 | ? Passing |

## 22.5 Services Layer

| Service Module | Responsibility |
|----------------|----------------|
| `base.py` | Shared utilities: `connection()`, `build_list_query()`, `now_iso()`, `parse_json()`, `dumps_json()`, `execute_update()` |
| `supplier.py` | Supplier CRUD + business rules |
| `customer.py` | Customer CRUD + CSV import |
| `shipping.py` | Shipping provider abstraction, rates, tracking, labels |
| `shipping/base.py` | Abstract `ShippingProvider` interface |
| `shipping/letmeship_client.py` | LetMeShip API client |
| `shipping/sendcloud_client.py` | SendCloud API client |
| `invoice.py` | Invoice CRUD + validation |
| `customs.py` | HS codes, duty calculation, declarations |
| `document.py` | Document upload, templates, metadata |
| `resource.py` | Resources CRUD |
| `eta/__init__.py` | ETA connector CRUD, invoice/receipt operations, batch submission |
| `eta/eta_client.py` | ETA HTTP client with OAuth2, retry, idempotency |
| `audit.py` | Centralized audit logging |
| `notification.py` | SMTP email sending with templates |
| `dashboard.py` | Live dashboard statistics aggregation |
| `search.py` | Unified search across all entities |
| `workflow.py` | Export workflow lifecycle with state machine |
| `knowledge_graph.py` | Graph CRUD, traversal, entity sync, Memory integration |
| `trade_intelligence.py` | Supplier/buyer analysis, trends, comparisons, reports |

## 22.6 Known Architectural Debt

## 22.7 Documentation Baseline

| Component | Status | Details |
|-----------|--------|---------|
| Master Document | ? `PLAN.md` | 1,746 lines, 27 sections � Single Source of Truth |
| Archive | ? `.kilo/plans/archive/` | 48 files + 2 directories � historical references only |
| Appendices | ? `docs/appendices/` | 9 files � long-form execution details |
| Standalone References | ? 19 files | ED, ADR, Contracts, Specs, EARP-001 package � independent |
| Cross-References | ? Valid | All active document references point to existing files |
| Code Modifications | ? Zero | No source code modified during consolidation |
| Architectural Drift | ? None | No boundary, responsibility, layer, dependency, or lifecycle changes |

**Consolidation Date:** 2026-07-29
**Closure Status:** CLOSED
**Closure Record:** `.kilo/plans/1785338639982-documentation-consolidation-closure-record.md`


| Debt | Location | Reference | Status |
|------|----------|-----------|--------|
| Raw SQL everywhere | `database.py`, routers | Section 9.9 | Accepted |
| No rate limiting | Missing | Section 4 (������) | Open |
| PostgreSQL migration path | Not started | Section 9.9 | Open |
| Root `alembic.ini` exists | Project root | N/A | Low |
| `__pycache__` directories | Throughout Python tree | N/A | Low |

---

# 23. Execution Governance

## 23.1 Evidence-Based Development

Every technical conclusion must be supported by objective evidence. Never assume what can be verified.

Permitted evidence sources include, but are not limited to:
- Backend logs
- API responses (request/response payloads and status codes)
- Browser Network tab data
- Console output
- Git diff
- Git history (commits, tags, baselines)
- Test results
- Screenshots (when appropriate)

Conclusions without supporting evidence are not valid and must not be used as the basis for decisions, closures, or acceptance.

## 23.2 Root Cause Analysis Standard

Every RCA must answer the following questions:
1. What happened?
2. Why did it happen?
3. Why was it not detected earlier?
4. Why is this the actual root cause?
5. What evidence proves it?

An RCA is not complete until all five questions are answered with supporting evidence.

## 23.3 Change Scope Policy

Every change must have a single responsibility. Do not mix unrelated bug fixes, refactoring, or new features in one implementation. Each change must address exactly one defect, one task, or one enhancement. Mixing scopes is prohibited.

## 23.4 Regression Policy

Every fix must be verified by:
1. Original failing scenario
2. Adjacent scenarios
3. Potentially affected functionality

All three verification levels must pass before the fix is considered complete.

## 23.5 Decision Gates

Mandatory execution gates that cannot be skipped:

- **Gate 1 ? Implementation Complete:** Code implementation is finished and ready for review. No commit yet.
- **Gate 2 ? Code Review Passed:** Code review is completed and approved.
- **Gate 3 ? Automated Tests Passed:** All automated tests pass.
- **Gate 4 ? Manual UAT Passed:** Manual UAT is completed successfully per the UAT checklist.
- **Gate 5 ? Project Owner Acceptance:** Project Owner formally accepts the deliverable.
- **Gate 6 ? Authorized Git Commit:** Changes are committed only after explicit authorization from the Project Owner.
- **Gate 7 ? Work Package Closed:** Work package is formally closed after all gates are satisfied.

No Work Package may be closed before all seven gates are satisfied.

## 23.6 Baseline Protection Policy

Approved baselines are immutable. Once a baseline has been approved, it must never be modified. Any future work shall begin as a new Work Package and produce a new approved baseline.

## 23.7 Project Execution Workflow

The mandatory execution lifecycle, in order:

Task ? Implementation ? Code Review ? Automated Tests ? Manual UAT ? Project Owner Acceptance ? Authorized Git Commit ? Work Package Closed ? Project Closure (when applicable)

## 23.8 Bug Handling Lifecycle

Every bug must follow this lifecycle:
1. Reproduce
2. Root Cause Analysis
3. Minimal Fix
4. Verify the Fix
5. Regression Check
6. Documentation
7. Close

Skipping any step is prohibited.

## 23.9 Work Package Completion Criteria

A Work Package is considered complete only when:
- All implementation is finished.
- All automated tests pass.
- Manual UAT is completed and passed.
- All evidence is documented.
- Project Owner acceptance is recorded.
- Git working tree is clean for the Work Package scope.
- Work Package is formally closed.

## 23.10 Prohibited Practices

The following practices are strictly prohibited:
- Closing a task before Manual UAT.
- Closing multiple unrelated defects in one change.
- Implementing changes before confirming the root cause.
- Declaring the project complete without Project Owner acceptance.
- Skipping any Decision Gate.
- Treating automated test success as a substitute for Manual UAT when Manual UAT is required.
- Closing a UAT checklist item without objective evidence.

## 23.11 Governing Principle

> "In case of any conflict between successful automated verification and actual user behavior, actual user behavior always takes precedence."

## 23.12 Kilo Operating Rules

When working on this repository with Kilo:
1. Read this document fully before any modification.
2. Read CURRENT_STATUS.md before starting any Work Package.
3. Read TECH_DEBT.md before starting any Work Package.
4. Always preserve architecture first.
5. Always verify before closing.
6. Always document major decisions in this document.
7. Never create duplicate implementations.
8. Never bypass testing.

---

# 24. Deployment & Operations

## 24.1 Requirements

- Python 3.11+
- Node.js 18+
- Docker / Docker Compose (recommended for production)

## 24.2 Docker Compose (Recommended)

### Setup

1. Create `.env` in project root.
2. Ensure all required variables are defined in `.env.example`.
3. In production, replace values with real secrets and do not upload `.env` to repository.

```bash
# Build and run services
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Backend Health: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

### Validation

```bash
# Verify services are running
curl http://localhost:8000/health
curl http://localhost:3000

# View logs
docker compose logs -f
```

### Troubleshooting

```bash
# Rebuild images without cache
docker compose build --no-cache

# Stop and remove containers
docker compose down

# Stop with data removal (deletes database)
docker compose down -v
```

## 24.3 Local Development (Without Docker)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 24.4 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key � 32+ chars | ? |
| `DATABASE_URL` | Database URL | ? |
| `ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) | ? |
| `DEBUG` | Debug mode | ? |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | ? |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | ? |
| `COOKIE_SECURE` | Secure cookies | ? |
| `COOKIE_SAMESITE` | SameSite policy | ? |
| `COOKIE_DOMAIN` | Cookie domain | ? |
| `SMTP_HOST` | SMTP server | ? |
| `SMTP_PORT` | SMTP port | ? |
| `SMTP_USER` | SMTP user | ? |
| `SMTP_PASSWORD` | SMTP password | ? |
| `SMTP_FROM` | Sender email address | ? |
| `SMTP_USE_TLS` | Use TLS | ? |
| `LETME_API_ID` | LetMeShip API ID | ? |
| `LETME_API_PASSWORD` | LetMeShip API password | ? |
| `SENDCLOUD_PUBLIC_KEY` | SendCloud public key | ? |
| `SENDCLOUD_SECRET_KEY` | SendCloud secret key | ? |
| `ETA_CLIENT_ID` | ETA client ID | ? |
| `ETA_CLIENT_SECRET` | ETA client secret | ? |
| `ETA_BASE_URL` | ETA base URL | ? |
| `VITE_API_URL` | Backend URL for built frontend | ? |

## 24.5 Docker Architecture

### Services

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| Backend | Built from `backend/Dockerfile` | 8000 | FastAPI backend |
| Frontend | Built from `frontend/Dockerfile` | 3000 | Nginx serving built frontend |

### Volumes

| Volume | Description |
|--------|-------------|
| `db-data` | SQLite database storage (`/app/data/nile_key.db`) |

### Health Checks

| Service | Check | Interval |
|---------|-------|----------|
| Backend | `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` | 30 seconds |
| Frontend | `pid=$(cat /var/run/nginx.pid 2>/dev/null); [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null || exit 1` | 30 seconds |

## 24.6 API Endpoints

| Service | Path |
|---------|------|
| Health | `/health` |
| Root | `/` |
| Docs | `/docs`, `/redoc` |
| OpenAPI | `/openapi.json` |
| Authentication | `/api/v1/auth/*` |
| Suppliers | `/api/v1/suppliers/*` |
| Customers | `/api/v1/customers/*` |
| Shipments | `/api/v1/shipping/*` |
| Invoices | `/api/v1/invoices/*` |
| Customs | `/api/v1/customs/*` |
| Documents | `/api/v1/documents/*` |
| Resources | `/api/v1/resources/*` |
| ETA | `/api/v1/eta/*` |
| Notifications | `/api/v1/notifications/*` |
| Audit | `/api/v1/audit/logs` |
| Workflows | `/api/v1/export-workflows` |
| Digital Export Manager | `/api/v1/digital-export-manager/*` |
| Knowledge Graph | `/api/v1/knowledge-graph/*` |
| Trade Intelligence | `/api/v1/trade-intelligence/*` |

---

# 25. Repository Architecture

## 25.1 Architecture Overview

```
nile-key-project/
??? PLAN.md                          # Master Roadmap v2.1 � Single Source of Truth
??? README.md                        # Project overview
??? backend/
?   ??? main.py                      # FastAPI entry point
?   ??? requirements.txt             # Dependencies
?   ??? .env.example                 # Environment template
?   ??? app/
?       ??? core/
?       ?   ??? config.py            # Settings
?       ?   ??? database.py          # SQLite init + schema
?       ?   ??? security.py          # JWT + password hashing
?       ??? routers/                 # API routers (thin controllers)
?       ??? schemas/                 # Pydantic models
?       ??? services/                # Business logic layer
?       ??? models/                  # SQLAlchemy models (if used)
??? frontend/
?   ??? package.json                 # Dependencies
?   ??? vite.config.ts               # Vite + React
?   ??? src/
?       ??? main.tsx                 # React entry point
?       ??? App.tsx                  # Route definitions
?       ??? pages/                   # 11 pages
?       ??? services/api.ts          # Axios client
?       ??? store/authStore.ts       # Zustand auth state
??? docs/
    ??? architecture/                # Architecture references
```

## 25.2 Dependency Map

- `main.py` ? `core/database`, `core/security`, `routers/*`
- Each router ? `core/database`, `core/security`, `schemas/*`
- Services ? `core/database`, `schemas/*`

## 25.3 Source of Truth Priority

Per PLAN.md Section 9.3, priority order (never reverse):

1. **Backend Pydantic Schemas** (`backend/app/schemas/`) � ? 18 modules defined
2. **FastAPI API Contract** � ? 16 registered routers in main.py
3. **Business Rules** � ? Implemented in service layer
4. **Database Schema** � ? Aligned via `init_db()` + Alembic
5. **Frontend Types** � ? Generated from OpenAPI
6. **Documentation** � ? Aligned after WP-41

## 25.4 Module Relationship

All routers depend on `core/database` (get_db) and `core/security` (for auth). No circular dependencies. Business logic lives in services layer, not routers.

---

# 26. Decision & Contract Index

## 26.1 Engineering Decisions (ED)

| ID | Document | Status |
|----|----------|--------|
| ED-WP30-001 | `.kilo/plans/ED-WP30-001.md` | Approved |
| ED-WP30-002 | `.kilo/plans/ED-WP30-002.md` | Approved |
| ED-WP32-001 | `.kilo/plans/ED-WP32-001.md` | Approved |

## 26.2 Executive Architecture Decisions (EAD)

| ID | Document | Status |
|----|----------|--------|
| EARP-001 | `.kilo/plans/earp-001/EAD.md` | Draft � Pending Approval |

## 26.3 Architecture Decision Records (ADR)

| ID | Document | Status |
|----|----------|--------|
| ADR-0001 | `docs/architecture/ADR-0001-shipments-legacy-columns.md` | Approved |

## 26.4 Contracts

| Contract | Document | Status |
|----------|----------|--------|
| Memory Contract | `.kilo/plans/MEMORY_CONTRACT.md` | Approved |
| Knowledge Ingestion Contract | `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` | Approved |
| Avatar Contract | `.kilo/plans/AVATAR_CONTRACT.md` | Approved |

## 26.5 Business Architecture

| Document | Status |
|----------|--------|
| `.kilo/plans/BA-ARCH-001.md` | Approved |
| `.kilo/plans/BA-IMPL-001.md` | Approved |
| `.kilo/plans/BA-WP-001.md` | Approved |
| `.kilo/plans/BA-ARCH-001-ADR-001.md` | Approved |
| `.kilo/plans/BA-ARCH-001-ADR-002.md` | Approved |
| `.kilo/plans/BA-ARCH-001-ADR-003.md` | Approved |

---

# 27. Appendix References

| Appendix | Location | Description |
|----------|----------|-------------|
| UAT Checklist | `docs/appendices/UAT_CHECKLIST.md` | Manual UAT verification checklist |
| UX Manual | `docs/appendices/OV-001-stage-6-ux-manual.md` | UX manual for OV-001 |
| Work Package Plan (Detailed) | `.kilo/plans/archive/WORK_PACKAGE_PLAN.md` | Detailed WP breakdowns with validation steps and rollback commands |
| WP-02 Completion Report | `docs/appendices/WP-02_COMPLETION_REPORT.md` | WP-02 completion report |
| UAT Runbook | `docs/appendices/wp42-uat-runbook.md` | UAT execution runbook |
| UAT Session Schedule | `docs/appendices/wp42-uat-session-schedule.md` | UAT session schedule |
| Owner Acceptance Certificate | `docs/appendices/wp42-owner-acceptance-certificate.md` | UAT evidence and acceptance |
| WP-33 Roadmap Verification | `docs/appendices/wp33e-final-roadmap-verification.md` | WP-33 final verification |
| WP-40 Closure Verification | `docs/appendices/wp40f-final-closure-and-baseline-verification.md` | WP-40 closure verification |
| WP-41 Documentation Verification | `docs/appendices/wp41-documentation-verification-report.md` | WP-41 documentation verification |

---

**��� �����:** 2026-07-29
**�������:** 2.2.0
**������:** ����� ������� ������ � Single Source of Truth
## 22.8 Repository Hygiene Baseline

| Component | Status | Details |
|-----------|--------|---------|
| Active Inventory | OK 426 files | Excluding build/run/artifact directories |
| Reference Integrity | OK Valid | 33/33 static imports valid; 2 broken doc references |
| Duplicates | OK 13 groups | 12 evidence PNG groups + 1 .env.example duplicate |
| Orphans | OK None | No proven orphan files after exhaustive usage checks |
| Source Modifications | OK Zero | No source code modified during audit |
| Cleanup Actions | OK None approved | No DELETE or mandatory ARCHIVE decisions |

**Audit Date:** 2026-07-30
**Closure Status:** CLOSED
**Closure Record:** `.kilo/plans/1785374443432-repository-hygiene-audit-closure-record.md`


