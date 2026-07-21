# WP-33 Specification: Trade Intelligence

**Work Package:** WP-33 — Trade Intelligence  
**Phase:** 2 — Intelligent Platform  
**Baseline:** 524c7339224792efb207d59f4ce2bbaba4ab4667  
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth  
**Engineering Decisions:** ED-WP33-001, ED-WP33-002, ED-WP33-003  
**Date:** 2026-07-20  
**Status:** Draft — Pending Approval  

---

## 1. Executive Summary

WP-33 implements the **Trade Intelligence** bounded context for the Digital Export Manager (DEM). Trade Intelligence provides analytical insights over existing platform entity data — specifically suppliers and buyers — enabling the DEM to discover trends, compare entities, and generate reports for decision-making.

Trade Intelligence is a read-only analytical layer that:
- Reads existing entity data through existing services and Knowledge Graph
- Produces analytical insights without modifying any data
- Integrates with Decision Engine, Execution Engine, Memory, Company Knowledge, and Dashboard
- Does NOT make business decisions
- Does NOT execute actions
- Does NOT modify entity data or Knowledge Graph

Per ED-WP33-001, the scope is limited to:
- Capability #9: Trade Intelligence (analysis, trends, comparisons)
- Capability #15: Supplier Intelligence (evaluation, suggestions)
- Capability #16: Buyer Intelligence (behavior, relationships)

Capability #13 (Opportunity Discovery) and Capability #14 (Market Analysis) are deferred to future Work Packages.

**Source:** PLAN.md Section 6.2, Section 7, Section 15.3, Section 16.3, Section 17; ED-WP33-001; ED-WP33-002; ED-WP33-003.

---

## 2. Scope

### 2.1 In Scope

| Component | Description | Source |
|-----------|-------------|--------|
| **Supplier Analysis** | Analyze supplier performance, comparisons, and trends | ED-WP33-001 |
| **Buyer Analysis** | Analyze buyer behavior, patterns, and relationships | ED-WP33-001 |
| **Market Trends** | Detect trends in entity data | ED-WP33-001 |
| **Comparisons** | Compare entities (suppliers, buyers) | ED-WP33-001 |
| **Report Generation** | Generate analytical reports from insights | ED-WP33-003 |
| **Service Layer** | Analytical services for suppliers, buyers, trends, comparisons, reports | ED-WP33-002, ED-WP33-003 |
| **API Layer** | FastAPI router exposing analysis endpoints | PLAN.md Section 9.10 |
| **Memory Integration** | Store and recall analysis results via MemoryProvider | ED-WP33-002 |
| **Audit Logging** | Log analysis requests via existing audit framework | PLAN.md Section 9.12 |
| **Pydantic Schemas** | Analysis request/response/insight/report schemas | PLAN.md Section 9.3 |

### 2.2 Explicitly Out of Scope

| Item | Reason | Source |
|------|--------|--------|
| **Opportunity Discovery** | Deferred to future WP per ED-WP33-001 | ED-WP33-001 |
| **Market Analysis (external)** | Deferred to future WP per ED-WP33-001 | ED-WP33-001 |
| **Decision making** | Decision Engine (WP-30D) owns decisions | ED-WP33-001 |
| **Action execution** | Execution Engine (WP-30C) owns execution | ED-WP33-001 |
| **Entity CRUD** | Entity Services own data modifications | ED-WP33-001 |
| **Knowledge Graph modification** | WP-32 owns graph mutations | ED-WP33-001 |
| **Memory modification by others** | WP-31 owns memory management | ED-WP33-001 |
| **External market data sources** | Not in current platform scope | PLAN.md Section 3.2 |
| **Graph visualization frontend** | Not mentioned in PLAN.md | PLAN.md |
| **LLM-powered reasoning** | Not mentioned in PLAN.md for WP-33 | PLAN.md Section 6.2 |

---

## 3. Objectives

1. Provide analytical insights over supplier and buyer data to support decision-making.
2. Enable the DEM to discover trends and patterns in entity relationships.
3. Integrate with existing intelligence components (Knowledge Graph, Memory, Company Knowledge) without modifying them.
4. Maintain strict read-only boundaries: no data modification, no decision-making, no execution.
5. Ensure all analysis operations are auditable via the existing audit framework.

**Source:** PLAN.md Section 6.2 Capability #9, Section 16.3; ED-WP33-001; ED-WP33-002; ED-WP33-003.

---

## 4. Functional Requirements

### FR-33.1: Supplier Analysis
The system MUST provide analytical insights for supplier entities including:
- Performance metrics over time
- Comparison with other suppliers
- Trend detection in supplier behavior
- Recommendations for supplier engagement

**Source:** ED-WP33-001, ED-WP33-003

### FR-33.2: Buyer Analysis
The system MUST provide analytical insights for buyer entities including:
- Behavior patterns
- Purchase trends
- Relationship analysis via Knowledge Graph
- Recommendations for buyer engagement

**Source:** ED-WP33-001, ED-WP33-003

### FR-33.3: Market Trends
The system MUST detect and report trends in entity data including:
- Temporal patterns
- Comparative trends
- Anomaly detection

**Source:** ED-WP33-001, ED-WP33-003

### FR-33.4: Comparisons
The system MUST support comparison operations between entities including:
- Supplier-to-supplier comparison
- Buyer-to-buyer comparison
- Gap analysis

**Source:** ED-WP33-001, ED-WP33-003

### FR-33.5: Report Generation
The system MUST generate reports from analysis results including:
- Supplier Analysis Report
- Buyer Analysis Report
- Market Trends Report
- Comparison Report

**Source:** ED-WP33-003

### FR-33.6: Memory Integration
The system MUST store analysis results in Memory and recall previous analyses when available.

**Source:** ED-WP33-002, ED-WP33-003

### FR-33.7: Audit Logging
The system MUST log all analysis requests via the existing audit framework.

**Source:** PLAN.md Section 9.12, ED-WP33-002

### FR-33.8: Graceful Degradation
The system MUST continue operation when optional dependencies are unavailable, logging warnings.

**Source:** PLAN.md Section 9.4, ED-WP33-002

---

## 5. Non-Functional Requirements

### NFR-33.1: Performance
- Analysis operations MUST complete within reasonable time bounds defined in Implementation Plan
- Cached analyses (via Memory) MUST be returned faster than fresh analyses
- System MUST NOT block on unavailable optional dependencies

**Source:** PLAN.md Section 9.13, ED-WP33-002

### NFR-33.2: Reliability
- Analysis failures MUST NOT propagate to Decision Engine or Execution Engine
- System MUST gracefully degrade when dependencies are unavailable
- All errors MUST be logged with appropriate diagnostics

**Source:** PLAN.md Section 9.4, ED-WP33-002

### NFR-33.3: Security
- All analysis endpoints MUST require authentication
- Authorization MUST follow existing role-based access control
- All inputs MUST be validated via Pydantic schemas
- Analysis results MUST be scoped to user permissions

**Source:** PLAN.md Section 9.12, ED-WP33-002

### NFR-33.4: Observability
- All analysis operations MUST be auditable
- Confidence scores MUST be included in all insights
- Data source attribution MUST be included in all insights
- Diagnostics MUST be available on request

**Source:** ED-WP33-003

### NFR-33.5: Compatibility
- MUST follow existing service-layer patterns
- MUST use existing audit framework
- MUST use existing MemoryProvider interface
- MUST use existing KnowledgeProvider interface
- MUST NOT break existing tests

**Source:** PLAN.md Section 9, ED-WP33-002

---

## 6. Architecture Overview

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────┐
│         Digital Export Manager (DEM)     │
│                                           │
│  ┌───────────────────────────────────┐  │
│  │       Intelligence Layer          │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │     Trade Intelligence      │  │  │
│  │  │         (WP-33)              │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │  Analysis Services    │  │  │  │
│  │  │  │  - SupplierAnalysis   │  │  │  │
│  │  │  │  - BuyerAnalysis      │  │  │  │
│  │  │  │  - TrendsDetection    │  │  │  │
│  │  │  │  - Comparisons        │  │  │  │
│  │  │  │  - ReportGeneration   │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 6.2 Layer Assignment
- **Layer:** Intelligence Layer
- **Position:** Above Knowledge Graph (WP-32) and Memory (WP-31), below Decision Engine (WP-30D)
- **Pattern:** Read-only analytical services, stateless, dependency-injected

**Source:** ED-WP33-001, ED-WP33-002

---

## 7. Component Responsibilities

### 7.1 Trade Intelligence Service (WP-33)
| Responsibility | Description |
|----------------|-------------|
| Supplier Analysis | Analyze supplier performance, trends, and comparisons |
| Buyer Analysis | Analyze buyer behavior, patterns, and relationships |
| Market Trends | Detect trends in entity data |
| Comparisons | Compare entities (suppliers, buyers) |
| Report Generation | Generate analytical reports |
| Memory Integration | Store and recall analysis results |
| Audit Logging | Log analysis requests |

### 7.2 Decision Engine (WP-30D)
| Responsibility | Description |
|----------------|-------------|
| Decision Making | Make business decisions based on analysis results |
| Requirement Definition | Define what analysis is needed |
| Result Consumption | Consume insights from WP-33 |

### 7.3 Execution Engine (WP-30C)
| Responsibility | Description |
|----------------|-------------|
| Task Execution | Execute analysis tasks defined by Mission Planner |
| Context Provision | Provide execution context to WP-33 |

### 7.4 Mission Planner (WP-30C)
| Responsibility | Description |
|----------------|-------------|
| Planning | Define analysis requirements in execution plans |
| Task Orchestration | Coordinate analysis tasks |

### 7.5 Knowledge Graph (WP-32)
| Responsibility | Description |
|----------------|-------------|
| Relationship Data | Provide entity relationship data |
| Query Interface | Expose query() and get_sources() methods |

### 7.6 Memory (WP-31)
| Responsibility | Description |
|----------------|-------------|
| Persistence | Store and recall analysis results |
| Caching | Provide cached insights |

### 7.7 Company Knowledge (WP-30F)
| Responsibility | Description |
|----------------|-------------|
| External Knowledge | Provide external knowledge context |
| Query Interface | Expose query() method |

### 7.8 Entity Services
| Responsibility | Description |
|----------------|-------------|
| Data Provision | Provide entity data (suppliers, customers, shipments, etc.) |
| CRUD Operations | Own all entity data modifications |

### 7.9 Dashboard (WP-21)
| Responsibility | Description |
|----------------|-------------|
| Display | Display analysis results and reports |
| Visualization | Render charts and widgets |

**Source:** ED-WP33-001, ED-WP33-002, ED-WP33-003

---

## 8. Public Interfaces

### 8.1 Supplier Analysis
| Field | Value |
|-------|-------|
| **Name** | analyze_supplier |
| **Purpose** | Analyze supplier performance and trends |
| **Consumer** | Decision Engine, Execution Engine, Dashboard |
| **Preconditions** | Supplier exists, Knowledge Graph available, Memory available |
| **Postconditions** | Analysis insights generated and stored |
| **Inputs** | supplier_id (int), analysis_type (enum), date_range (optional) |
| **Outputs** | analysis_id, insights, recommendations, confidence_score |
| **Failure Conditions** | Supplier not found, dependency unavailable |

### 8.2 Buyer Analysis
| Field | Value |
|-------|-------|
| **Name** | analyze_buyer |
| **Purpose** | Analyze buyer behavior and patterns |
| **Consumer** | Decision Engine, Execution Engine, Dashboard |
| **Preconditions** | Buyer exists, Knowledge Graph available, Memory available |
| **Postconditions** | Analysis insights generated and stored |
| **Inputs** | buyer_id (int), analysis_type (enum), date_range (optional) |
| **Outputs** | analysis_id, insights, recommendations, confidence_score |
| **Failure Conditions** | Buyer not found, dependency unavailable |

### 8.3 Market Trends
| Field | Value |
|-------|-------|
| **Name** | detect_trends |
| **Purpose** | Detect trends in entity data |
| **Consumer** | Decision Engine, Execution Engine, Dashboard |
| **Preconditions** | Entity data available, Knowledge Graph available |
| **Postconditions** | Trends identified and reported |
| **Inputs** | entity_type (enum), trend_parameters (object) |
| **Outputs** | trends, patterns, confidence_score |
| **Failure Conditions** | Insufficient data, dependency unavailable |

### 8.4 Comparisons
| Field | Value |
|-------|-------|
| **Name** | compare_entities |
| **Purpose** | Compare multiple entities |
| **Consumer** | Decision Engine, Execution Engine, Dashboard |
| **Preconditions** | All entities exist, sufficient data available |
| **Postconditions** | Comparison results generated |
| **Inputs** | entity_ids (array), comparison_criteria (object) |
| **Outputs** | comparison_results, recommendations |
| **Failure Conditions** | Entities not found, insufficient data |

### 8.5 Report Generation
| Field | Value |
|-------|-------|
| **Name** | generate_report |
| **Purpose** | Generate analytical report from insights |
| **Consumer** | Dashboard, Decision Engine |
| **Preconditions** | Analysis results available |
| **Postconditions** | Report generated |
| **Inputs** | analysis_ids (array), report_type (enum) |
| **Outputs** | report_document, metadata |
| **Failure Conditions** | No analysis results available |

**Source:** ED-WP33-003

---

## 9. Data Contracts

### 9.1 Input DTO

#### Required Fields
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| entity_id | integer | Entity to analyze | > 0 |
| analysis_type | enum | supplier \| buyer \| market | Must be valid enum value |
| requested_by | string | Consumer identifier | Non-empty string |

#### Optional Fields
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| date_range | object | {start, end} dates | start < end, valid dates |
| parameters | object | Analysis-specific parameters | Valid JSON object |
| correlation_id | string | Request tracing | UUID format if present |

**Source:** ED-WP33-003

### 9.2 Output DTO

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| analysis_id | string | Unique analysis identifier (UUID) |
| insights | array | List of Insight objects |
| generated_at | datetime | ISO-8601 timestamp |
| confidence | float | Overall confidence score (0.0-1.0) |

#### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| recommendations | array | Suggested actions |
| limitations | array | Analysis constraints |
| data_sources | array | Sources used in analysis |
| provenance | object | Data lineage information |
| diagnostics | object | Performance metrics |

**Source:** ED-WP33-003

### 9.3 Error DTO

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| error_code | string | Machine-readable error code |
| category | string | validation \| dependency \| internal |
| message | string | Human-readable description |
| retryable | boolean | Whether caller can retry |
| caller_action | string | What caller should do |

#### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| details | object | Additional context |
| correlation_id | string | Request tracing ID |

**Source:** ED-WP33-003

---

## 10. Insight Model

### 10.1 Mandatory Fields
| Field | Type | Description |
|-------|------|-------------|
| finding | string | Core insight or discovery |
| confidence | float | Reliability score (0.0-1.0) |
| evidence | array | Supporting data points |
| sources | array | Data source identifiers |
| timestamp | datetime | When analysis was performed |
| analysis_id | string | Unique analysis identifier |

### 10.2 Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| recommendations | array | Suggested actions |
| limitations | array | Analysis constraints |
| explanation | string | Detailed reasoning |
| impact | string | Business impact assessment |
| urgency | enum | low \| medium \| high |

### 10.3 Confidence Representation
- Range: 0.0 (no confidence) to 1.0 (full confidence)
- Derived from: data quality, source reliability, analysis method
- MUST be included in every insight

### 10.4 Evidence Representation
- Array of data points supporting the finding
- Each evidence item MUST include: source_id, data_point, timestamp
- MUST NOT include raw database records (data ownership)

### 10.5 Source Attribution
- All data sources MUST be attributed
- Sources: Knowledge Graph, Memory, Company Knowledge, Entity Services
- Format: source_type + source_id + accessed_at

**Source:** ED-WP33-003

---

## 11. Report Contracts

### 11.1 Supplier Analysis Report
| Field | Value |
|-------|-------|
| **Purpose** | Comprehensive supplier performance analysis |
| **Audience** | Decision Engine, Management |
| **Required Sections** | Executive Summary, Supplier Metrics, Trends, Recommendations |
| **Optional Sections** | Competitive Analysis, Risk Assessment |
| **Export Formats** | PDF, CSV |
| **Ownership** | WP-33 |

### 11.2 Buyer Analysis Report
| Field | Value |
|-------|-------|
| **Purpose** | Customer behavior and pattern analysis |
| **Audience** | Decision Engine, Management |
| **Required Sections** | Executive Summary, Customer Segments, Behavior Patterns, Recommendations |
| **Optional Sections** | Lifetime Value Analysis, Churn Prediction |
| **Export Formats** | PDF, CSV |
| **Ownership** | WP-33 |

### 11.3 Market Trends Report
| Field | Value |
|-------|-------|
| **Purpose** | Trend detection in entity data |
| **Audience** | Decision Engine, Management |
| **Required Sections** | Executive Summary, Trends Detected, Statistical Summary, Recommendations |
| **Optional Sections** | Forecasting, Anomaly Detection |
| **Export Formats** | PDF, CSV |
| **Ownership** | WP-33 |

### 11.4 Comparison Report
| Field | Value |
|-------|-------|
| **Purpose** | Comparison between specified entities |
| **Audience** | Decision Engine, Management |
| **Required Sections** | Executive Summary, Entity Comparison, Gap Analysis, Recommendations |
| **Optional Sections** | Benchmarking, Best Practices |
| **Export Formats** | PDF, CSV |
| **Ownership** | WP-33 |

**Source:** ED-WP33-003

---

## 12. Integration Contracts

### 12.1 Decision Engine (WP-30D)
| Field | Value |
|-------|-------|
| **Purpose** | Consumes analysis results for decision-making |
| **Initiator** | Decision Engine |
| **Consumer** | WP-33 |
| **Dependency Direction** | Decision Engine → WP-33 |
| **Allowed Calls** | analyze_supplier(), analyze_buyer(), detect_trends(), compare_entities(), generate_report() |
| **Forbidden Calls** | Direct data modification, entity CRUD, decision execution |
| **Request Contract** | Input DTO per Section 9.1 |
| **Response Contract** | Output DTO per Section 9.2 |
| **Failure Contract** | Error DTO per Section 9.3 |
| **Ownership Boundary** | Decision Engine owns decisions; WP-33 owns insights |

### 12.2 Execution Engine (WP-30C)
| Field | Value |
|-------|-------|
| **Purpose** | Executes analysis tasks |
| **Initiator** | Execution Engine |
| **Consumer** | WP-33 |
| **Dependency Direction** | Execution Engine → WP-33 |
| **Allowed Calls** | perform_analysis() |
| **Forbidden Calls** | Business logic execution, state changes |
| **Request Contract** | Input DTO per Section 9.1 |
| **Response Contract** | Output DTO per Section 9.2 |
| **Failure Contract** | Error DTO per Section 9.3 |
| **Ownership Boundary** | Execution Engine owns execution; WP-33 owns analysis |

### 12.3 Mission Planner (WP-30C)
| Field | Value |
|-------|-------|
| **Purpose** | Plans analysis tasks |
| **Initiator** | Mission Planner |
| **Consumer** | WP-33 |
| **Dependency Direction** | Mission Planner → WP-33 |
| **Allowed Calls** | define_analysis_requirements() |
| **Forbidden Calls** | Direct execution |
| **Request Contract** | Analysis requirements object |
| **Response Contract** | Analysis plan |
| **Failure Contract** | Error DTO per Section 9.3 |
| **Ownership Boundary** | Mission Planner owns planning; WP-33 owns analysis methods |

### 12.4 Knowledge Graph (WP-32)
| Field | Value |
|-------|-------|
| **Purpose** | Provides relationship data |
| **Initiator** | WP-33 |
| **Consumer** | WP-32 |
| **Dependency Direction** | WP-33 → WP-32 |
| **Allowed Calls** | query(), get_sources() |
| **Forbidden Calls** | Direct node/edge modification |
| **Request Contract** | KnowledgeQuery per WP-30F |
| **Response Contract** | KnowledgeQueryResponse per WP-30F |
| **Failure Contract** | Continue with entity data only; log warning |
| **Ownership Boundary** | WP-32 owns graph; WP-33 reads graph |

### 12.5 Memory (WP-31)
| Field | Value |
|-------|-------|
| **Purpose** | Stores and recalls analysis history |
| **Initiator** | WP-33 |
| **Consumer** | WP-31 |
| **Dependency Direction** | WP-33 → WP-31 |
| **Allowed Calls** | recall(), store() |
| **Forbidden Calls** | Direct data deletion, forced forgetting |
| **Request Contract** | MemoryProvider interface per WP-31 |
| **Response Contract** | Memory items per WP-31 |
| **Failure Contract** | Continue without caching; log warning |
| **Ownership Boundary** | WP-31 owns memory; WP-33 uses memory |

### 12.6 Company Knowledge (WP-30F)
| Field | Value |
|-------|-------|
| **Purpose** | Provides external knowledge context |
| **Initiator** | WP-33 |
| **Consumer** | WP-30F |
| **Dependency Direction** | WP-33 → WP-30F |
| **Allowed Calls** | query() |
| **Forbidden Calls** | Direct knowledge modification |
| **Request Contract** | KnowledgeQuery per WP-30F |
| **Response Contract** | KnowledgeQueryResponse per WP-30F |
| **Failure Contract** | Continue with internal data only; log warning |
| **Ownership Boundary** | WP-30F owns knowledge; WP-33 queries knowledge |

### 12.7 Dashboard (WP-21)
| Field | Value |
|-------|-------|
| **Purpose** | Displays analysis results |
| **Initiator** | WP-33 |
| **Consumer** | Dashboard |
| **Dependency Direction** | WP-33 → Dashboard |
| **Allowed Calls** | API responses via FastAPI router |
| **Forbidden Calls** | Direct database access, business logic |
| **Request Contract** | REST API endpoints |
| **Response Contract** | JSON responses per API schema |
| **Failure Contract** | Continue without dashboard; log warning |
| **Ownership Boundary** | Dashboard owns display; WP-33 owns data |

**Source:** ED-WP33-002, ED-WP33-003

---

## 13. Dependency Contracts

### 13.1 Knowledge Graph (WP-32)
| Field | Value |
|-------|-------|
| **Required Inputs** | Entity relationships, entity types |
| **Expected Outputs** | Relationship data, entity metadata |
| **Guarantees** | Read-only access, no modification |
| **Assumptions** | Graph is populated with entity data |
| **Failure Behavior** | Continue with entity data only; log warning |

### 13.2 Memory (WP-31)
| Field | Value |
|-------|-------|
| **Required Inputs** | Previous analyses, stored insights |
| **Expected Outputs** | Cached analysis results |
| **Guarantees** | Persistent storage, recall by key |
| **Assumptions** | Memory available and operational |
| **Failure Behavior** | Continue without caching; log warning |

### 13.3 Company Knowledge (WP-30F)
| Field | Value |
|-------|-------|
| **Required Inputs** | Knowledge queries, context |
| **Expected Outputs** | External knowledge items |
| **Guarantees** | Read-only access |
| **Assumptions** | Knowledge base populated |
| **Failure Behavior** | Continue with internal data only; log warning |

### 13.4 Entity Services
| Field | Value |
|-------|-------|
| **Required Inputs** | Entity IDs, entity types |
| **Expected Outputs** | Entity records, attributes |
| **Guarantees** | Read-only access |
| **Assumptions** | Entity data exists and is valid |
| **Failure Behavior** | Return error; analysis cannot proceed |

### 13.5 Decision Engine (WP-30D)
| Field | Value |
|-------|-------|
| **Required Inputs** | Analysis requests, requirements |
| **Expected Outputs** | Insights, recommendations |
| **Guarantees** | Non-blocking, asynchronous |
| **Assumptions** | Decision Engine provides clear requirements |
| **Failure Behavior** | Return error; do not retry automatically |

### 13.6 Execution Engine (WP-30C)
| Field | Value |
|-------|-------|
| **Required Inputs** | Analysis tasks, execution context |
| **Expected Outputs** | Analysis results |
| **Guarantees** | Task execution, result delivery |
| **Assumptions** | Execution Engine provides execution context |
| **Failure Behavior** | Return error; task marked as failed |

### 13.7 Dashboard (WP-21)
| Field | Value |
|-------|-------|
| **Required Inputs** | Analysis results, reports |
| **Expected Outputs** | Display data, widgets |
| **Guarantees** | Read-only access |
| **Assumptions** | Dashboard available and operational |
| **Failure Behavior** | Continue without dashboard; log warning |

**Source:** ED-WP33-002, ED-WP33-003

---

## 14. State Model

### 14.1 State Classification
**WP-33 is STATELESS.**

### 14.2 Justification
1. **Project Pattern:** All services in the project are stateless (Customer, Supplier, Shipping, ETA, Customs)
2. **PLAN.md Section 9.9:** "Database follows Backend. Backend never follows Database."
3. **ED-WP33-001:** WP-33 does not own persistent data
4. **PLAN.md Section 9.8:** "Prefer isolated modules."

### 14.3 Caching Strategy
| Aspect | Decision |
|--------|----------|
| **Owner** | WP-33 (cache consumer), Memory (WP-31) (cache provider) |
| **Lifetime** | Analysis-dependent (default: 24 hours) |
| **Invalidation** | Explicit invalidation on new analysis |
| **Storage Location** | Memory (WP-31) |

### 14.4 No Persistent Storage
WP-33 MUST NOT own persistent database tables. All persistence is via Memory (WP-31) or Entity Services.

**Source:** ED-WP33-002, ED-WP33-003

---

## 15. Validation Rules

### 15.1 Input Validation
- All inputs MUST be validated via Pydantic schemas
- entity_id MUST be positive integer
- analysis_type MUST be valid enum value
- date_range MUST have start < end
- parameters MUST be valid JSON object

### 15.2 Business Validation
- Entity MUST exist before analysis
- User MUST have permission to analyze entity
- Analysis parameters MUST be within acceptable ranges

### 15.3 Output Validation
- All insights MUST include confidence score
- All insights MUST include source attribution
- All reports MUST include timestamp
- Error responses MUST include error_code, category, and caller_action

**Source:** PLAN.md Section 9.3, ED-WP33-003

---

## 16. Error Handling

### 16.1 Error Categories
| Category | Description | Retryable | Caller Action |
|----------|-------------|-----------|---------------|
| validation | Invalid input parameters | No | Fix input and retry |
| dependency | Required dependency unavailable | No | Notify user; check system health |
| internal | Analysis processing error | No | Retry with different parameters |
| not_found | Entity not found | No | Verify entity ID |
| permission | User lacks permission | No | Request access |

### 16.2 Failure Modes
| Failure | Behavior |
|---------|----------|
| Knowledge Graph unavailable | Continue with entity data only; log warning |
| Memory unavailable | Continue without caching; log warning |
| Company Knowledge unavailable | Continue with internal data only; log warning |
| Entity Service unavailable | Return error; analysis cannot proceed |

### 16.3 Graceful Degradation
- Optional dependencies failing MUST NOT block analysis
- Required dependencies failing MUST return error
- All failures MUST be logged with diagnostics

**Source:** PLAN.md Section 9.4, ED-WP33-002, ED-WP33-003

---

## 17. Security Requirements

### 17.1 Authentication
- All analysis endpoints MUST require authentication
- JWT tokens MUST be validated
- Expired tokens MUST be rejected

### 17.2 Authorization
- Role-based access control MUST be enforced
- Users MUST only analyze entities they have permission to access
- Admin roles MAY access all entities

### 17.3 Input Security
- All inputs MUST be validated
- SQL injection MUST be prevented (use parameterized queries)
- No hardcoded secrets
- No trust in client input

### 17.4 Data Security
- Analysis results MUST be scoped to user permissions
- Sensitive data MUST NOT be exposed in error messages
- Audit logging MUST include user context

**Source:** PLAN.md Section 9.12, ED-WP33-002

---

## 18. Performance Requirements

### 18.1 Response Times
| Operation | Target | Justification |
|-----------|--------|---------------|
| Supplier Analysis | < 2s | Defined in Implementation Plan |
| Buyer Analysis | < 2s | Defined in Implementation Plan |
| Market Trends | < 3s | Defined in Implementation Plan |
| Comparisons | < 2s | Defined in Implementation Plan |
| Report Generation | < 5s | Defined in Implementation Plan |

### 18.2 Throughput
- Support concurrent analysis requests
- No hard limit on concurrent users (scale horizontally)

### 18.3 Resource Usage
- Memory usage MUST NOT exceed acceptable limits
- CPU usage MUST NOT exceed acceptable limits
- Caching MUST NOT cause memory leaks

**Source:** PLAN.md Section 9.13, ED-WP33-002

---

## 19. Acceptance Criteria

### AC-33.1: Supplier Analysis
- [ ] Supplier analysis returns valid insights with confidence scores
- [ ] Supplier analysis uses Knowledge Graph for relationship data
- [ ] Supplier analysis stores results in Memory
- [ ] Supplier analysis is auditable

### AC-33.2: Buyer Analysis
- [ ] Buyer analysis returns valid insights with confidence scores
- [ ] Buyer analysis uses Knowledge Graph for relationship data
- [ ] Buyer analysis stores results in Memory
- [ ] Buyer analysis is auditable

### AC-33.3: Market Trends
- [ ] Market trends detects patterns in entity data
- [ ] Market trends returns confidence scores
- [ ] Market trends is auditable

### AC-33.4: Comparisons
- [ ] Comparisons returns valid comparison results
- [ ] Comparisons supports multiple entity types
- [ ] Comparisons is auditable

### AC-33.5: Report Generation
- [ ] Reports are generated in PDF format
- [ ] Reports are generated in CSV format
- [ ] Reports include all required sections
- [ ] Reports are owned by WP-33

### AC-33.6: Integration
- [ ] Decision Engine can consume analysis results
- [ ] Execution Engine can execute analysis tasks
- [ ] Dashboard can display analysis results
- [ ] Knowledge Graph integration works
- [ ] Memory integration works
- [ ] Company Knowledge integration works

### AC-33.7: Boundaries
- [ ] WP-33 never modifies entity data
- [ ] WP-33 never makes business decisions
- [ ] WP-33 never executes actions
- [ ] WP-33 never modifies Knowledge Graph
- [ ] WP-33 never modifies Memory owned by others

### AC-33.8: Quality
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All security tests pass
- [ ] Performance tests meet thresholds
- [ ] No regressions in existing tests

**Source:** PLAN.md Section 16.3, ED-WP33-001, ED-WP33-002, ED-WP33-003

---

## 20. Testing Requirements

### 20.1 Unit Tests
- Test each analysis service independently
- Mock all dependencies
- Cover success and failure paths
- Target: 30+ unit tests

### 20.2 Integration Tests
- Test API endpoints with test client
- Test integration with Knowledge Graph
- Test integration with Memory
- Test integration with Company Knowledge
- Test authentication and authorization
- Target: 20+ integration tests

### 20.3 Performance Tests
- Test analysis response times
- Test concurrent requests
- Test caching effectiveness
- Target: All operations within defined thresholds

### 20.4 Security Tests
- Test authentication requirements
- Test authorization rules
- Test input validation
- Test audit logging
- Target: All security controls verified

### 20.5 Regression Tests
- Full test suite must pass
- No existing tests broken
- Target: 100% existing tests pass

**Source:** PLAN.md Section 10.4, ED-WP33-002

---

## 21. Traceability

### 21.1 PLAN.md References
| PLAN.md Section | Reference |
|-----------------|-----------|
| Section 6.2 | Capability #9: Trade Intelligence |
| Section 7 | WP-33: Trade Intelligence — ذكاء السوق والموردين والعملاء |
| Section 15.3 | WP-33: Trade Intelligence |
| Section 16.3 | Trade Intelligence يقدم تقارير |
| Section 17 | Trade Intelligence → Intelligence Engine → WP-42 |
| Section 9.3 | Source of Truth: Pydantic Schemas |
| Section 9.9 | Database Rules |
| Section 9.10 | API Rules |
| Section 9.12 | Security Rules |
| Section 9.13 | Performance Rules |
| Section 10.4 | Testing Rules |
| Section 10.8 | Quality Gates |

### 21.2 Engineering Decision References
| Decision | Title | Status |
|----------|-------|--------|
| ED-WP33-001 | Capability Boundaries | APPROVED |
| ED-WP33-002 | Integration Contracts | APPROVED |
| ED-WP33-003 | Public Interface & Data Contracts | APPROVED |

### 21.3 Work Package Dependencies
| WP | Description | Status |
|----|-------------|--------|
| WP-30B | Session Management + Mission Lifecycle | Complete |
| WP-30C | Task Planner + Execution Engine | Complete |
| WP-30D | Decision Engine | Complete |
| WP-30F | Company Knowledge Layer | Complete |
| WP-31 | AI Memory | Complete |
| WP-32 | Knowledge Graph | Complete |

**Source:** PLAN.md Section 7, ED-WP33-001, ED-WP33-002, ED-WP33-003

---

## 22. Open Issues

### 22.1 Blocking Issues
None. All architectural decisions have been made in ED-WP33-001, ED-WP33-002, and ED-WP33-003.

### 22.2 Non-Blocking Issues
| Issue | Resolution Path |
|-------|-----------------|
| Exact method signatures | Defined in Implementation Plan |
| Exact data schemas | Defined in Implementation Plan using Pydantic |
| Exact report formats | Defined in Implementation Plan |
| Exact confidence calculation | Defined in Implementation Plan |
| Exact caching parameters | Defined in Implementation Plan |

---

## 23. Document Authority

This document defines the specification for WP-33.

All implementation tasks, technical designs, and code changes for WP-33 MUST derive from this document and the referenced Engineering Decisions.

Any deviation requires a documented architectural decision recorded in the Architectural Decision Log (PLAN.md Section 13) with explicit rationale.

**Status:** Draft — Pending Approval

---

## 24. References

- `PLAN.md` Section 6.2 — Capability #9: Trade Intelligence
- `PLAN.md` Section 7 — Work Package execution order
- `PLAN.md` Section 9.3 — Source of Truth: Pydantic Schemas
- `PLAN.md` Section 9.9 — Database Rules
- `PLAN.md` Section 9.10 — API Rules
- `PLAN.md` Section 9.12 — Security Rules
- `PLAN.md` Section 10.4 — Testing Rules
- `PLAN.md` Section 10.8 — Quality Gates
- `PLAN.md` Section 14.1 — Implementation Rules
- `PLAN.md` Section 15.3 — WP-33 status
- `PLAN.md` Section 16.3 — Phase 2 exit criteria
- `.kilo/plans/ED-WP33-001.md` — Capability Boundaries
- `.kilo/plans/ED-WP33-002.md` — Integration Contracts
- `.kilo/plans/ED-WP33-003.md` — Public Interface & Data Contracts
- `backend/app/agent/knowledge/provider.py` — `KnowledgeProvider` ABC
- `backend/app/agent/knowledge/registry.py` — `KnowledgeProviderRegistry`
- `backend/app/agent/memory/interface.py` — `MemoryProvider` ABC
- `backend/app/services/base.py` — Service layer utilities
- `backend/app/services/audit.py` — Audit logging
- `backend/app/core/database.py` — Database initialization pattern
- `backend/main.py` — Application entry point and router registration
- `backend/app/routers/auth.py` — `get_current_user`, `require_role` dependencies
