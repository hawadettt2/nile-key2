# DEM Architecture Explorer v2 — Architecture Graph Schema

## Status

**Phase:** 1 — Architecture Graph / Data Model  
**Purpose:** Define the canonical data contract that drives all Explorer levels and views.  
**Runtime impact:** None. Documentation/data-model only.  
**Authority:** `ARCHITECTURE_EXPLORER_V2_PLAN.md` + `ARCHITECTURE_EXPLORER_V2_EVIDENCE_INVENTORY.md`  
**Schema version:** `1.0`

## 1. Design principles

1. **Evidence is authoritative.** A graph element is not considered true merely because it is useful for a diagram.
2. **The graph is the source model; the UI is a projection.** SVG/canvas/HTML must not become the architecture source of truth.
3. **Identity, meaning, level, type, and status are separate dimensions.** They must never be overloaded into one field.
4. **Relationships are first-class architecture knowledge.** An edge carries semantic meaning and evidence.
5. **English is technical identity.** Arabic is functional meaning/explanation.
6. **Runtime and planned architecture must coexist without being conflated.** Status is mandatory for every node and edge.
7. **Repository evidence is explicit.** Exact paths are recorded whenever implementation identity is known.
8. **Unknown is preferable to invented.** Missing evidence is represented as `unknown`/`unverified`, not inferred as fact.
9. **The model is level-independent.** A node has one identity and may be projected at multiple Explorer levels.
10. **No application runtime code is required by this schema.** This phase is documentation/data-model only.

## 2. Top-level graph document

```text
ArchitectureGraph
├── schema_version
├── graph_id
├── title
├── description
├── source
│   ├── repository
│   ├── branch
│   ├── evidence_baseline
│   └── generated_at
├── nodes[]
├── edges[]
└── validation
    ├── required_fields
    ├── controlled_vocabularies
    └── notes
```

### Required graph metadata

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | yes | Version of this data contract. |
| `graph_id` | string | yes | Stable graph identifier. |
| `title` | string | yes | Human-readable graph title. |
| `description` | string | yes | Scope of the graph dataset. |
| `source.repository` | string | yes | Repository identity. |
| `source.branch` | string | yes | Repository branch used as evidence. |
| `source.evidence_baseline` | string | yes | Evidence document/commit used to build the dataset. |
| `source.generated_at` | ISO-8601 string | yes | Dataset generation timestamp. |
| `nodes` | array | yes | Architecture nodes. |
| `edges` | array | yes | Architecture relationships. |
| `validation` | object | yes | Contract-level validation metadata. |

## 3. Node contract

A node represents one architectural identity. It is not a visual box.

```text
Node
├── id
├── technical_name
├── arabic_meaning
├── arabic_description
├── type
├── levels[]
├── status
├── responsibilities[]
├── non_responsibilities[]
├── paths[]
├── evidence[]
├── parent_ids[]
├── tags[]
└── metadata
```

### Node required fields

| Field | Type | Required | Rule |
|---|---|---:|---|
| `id` | string | yes | Stable, machine-readable identity. Must remain stable if the display label changes. |
| `technical_name` | string | yes | Exact repository/architecture technical identity in English. |
| `arabic_meaning` | string | yes | Functional Arabic meaning; not a replacement for technical identity. |
| `type` | enum | yes | Architectural classification. |
| `levels` | integer[] | yes | One or more Explorer levels where the node is legitimately projected. Values: `0..3`. |
| `status` | enum | yes | Current evidence state. |
| `responsibilities` | string[] | yes | What the node owns/does. May be empty only when status is external and evidence is unavailable. |
| `non_responsibilities` | string[] | yes | Explicit boundary where known; may be empty when not established. |
| `paths` | string[] | yes | Exact repository paths when implemented/documented; empty for purely conceptual/external nodes. |
| `evidence` | EvidenceRef[] | yes | Evidence supporting the node's existence/status/meaning. |
| `parent_ids` | string[] | yes | Structural containment parents; empty at universe/root level. |
| `tags` | string[] | yes | Search/filter metadata. |
| `metadata` | object | yes | Extensible non-semantic metadata; must not contradict the core contract. |

## 4. Node types

Controlled vocabulary for `type`:

- `universe`
- `business_boundary`
- `application`
- `frontend`
- `api_boundary`
- `backend`
- `router`
- `schema_contract`
- `agent_subsystem`
- `agent_tool`
- `orchestration`
- `knowledge`
- `research`
- `business_capability`
- `business_service`
- `core_infrastructure`
- `security`
- `credential_management`
- `audit`
- `monitoring`
- `scheduler`
- `persistence`
- `database`
- `model_structure`
- `external_system`
- `governance`
- `planned_architecture`
- `reserved_structure`

A node must not use `business_service` merely because its file is under `services/`; the classification must reflect its architectural role.

## 5. Node status

Controlled vocabulary for `status`:

- `implemented_runtime` — verified as part of current runtime architecture.
- `implemented_non_primary` — implemented in repository but not established as the primary runtime path.
- `governance_documented` — architecture/contract/governance concept supported by authoritative documentation rather than runtime implementation.
- `planned_future` — explicitly documented future architecture.
- `reserved_minimal` — repository structure exists but is intentionally minimal/reserved and must not be presented as a completed subsystem.
- `external` — outside the repository and treated as an external dependency/system.
- `unverified` — observed or proposed but not yet sufficiently evidenced; must not be treated as runtime truth.

## 6. Evidence reference contract

```text
EvidenceRef
├── kind
├── path
├── detail
└── authority
```

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `kind` | enum | yes | `repository_file`, `repository_directory`, `governance_document`, `adr`, `runtime_wiring`, `external_reference`. |
| `path` | string | yes | Repository path or documented external reference identity. |
| `detail` | string | yes | What the evidence proves. |
| `authority` | enum | yes | `primary`, `supporting`, or `context`. |

Evidence must state what it proves, not merely name a file.

## 7. Edge contract

An edge represents a semantic relationship between two existing node identities.

```text
Edge
├── id
├── source
├── target
├── relation_type
├── direction
├── status
├── evidence[]
├── data
└── metadata
```

### Edge required fields

| Field | Type | Required | Rule |
|---|---|---:|---|
| `id` | string | yes | Stable edge identity. |
| `source` | string | yes | Existing node ID. |
| `target` | string | yes | Existing node ID. |
| `relation_type` | enum | yes | Controlled semantic relationship. |
| `direction` | enum | yes | `directed` or `undirected`; use directed for flow/dependency. |
| `status` | enum | yes | Same status vocabulary as nodes. |
| `evidence` | EvidenceRef[] | yes | Evidence supporting the relationship. |
| `data` | object | yes | Optional structured information about what crosses the edge. |
| `metadata` | object | yes | Extensible metadata. |

## 8. Edge relation types

Controlled vocabulary for `relation_type`:

- `contains` — structural decomposition/ownership.
- `exposes` — exposes an interface/API boundary.
- `routes_to` — request routing from a router/boundary to a downstream component.
- `control_flow` — runtime execution/control handoff.
- `invokes` — one implementation directly invokes another.
- `delegates_to` — responsibility is delegated to another component/service.
- `depends_on` — technical dependency without a more precise flow classification.
- `produces` — creates a plan, task, decision, result, or other structured artifact consumed by a downstream architectural component.
- `data_flow` — structured data crosses a boundary.
- `knowledge_flow` — knowledge/context is supplied or consumed.
- `memory_flow` — memory/context is read or written.
- `external_integration` — integration with an external system/provider.
- `persists_to` — runtime data is persisted to a datastore.
- `reads_from` — runtime reads from a datastore/source.
- `writes_to` — runtime writes to a datastore/source.
- `governed_by` — implementation/boundary is governed by a contract/ADR.
- `audited_by` — activity is connected to audit capability.
- `monitored_by` — activity is connected to monitoring capability.
- `secured_by` — boundary/capability is protected by security control.
- `scheduled_by` — activity is controlled by a scheduler.
- `implements` — concrete implementation realizes an architectural capability.
- `planned_migration_to` — documented future migration relationship; never a current runtime dependency.

Do not use `depends_on` when a more precise relation is evidenced.

## 9. Relationship semantics and boundaries

### Structural

```text
A --contains--> B
```

Means B is architecturally inside A. It does **not** mean A calls B at runtime.

### Runtime

```text
A --control_flow/invokes/delegates_to--> B
```

Means repository/runtime evidence supports the handoff.

### Artifact production

```text
A --produces--> B
```

Means A creates or prepares a structured artifact that becomes the input to B. It does not by itself claim that A directly invokes B at runtime.

### Data / knowledge

```text
A --data_flow/knowledge_flow/memory_flow--> B
```

Means the graph is documenting the information crossing the boundary, not merely a software dependency.

### Future architecture

```text
SQLite --planned_migration_to--> PostgreSQL
```

This must carry `planned_future` status and evidence from the governing ADR. It must never be rendered as a current runtime edge.

## 10. Level projection rules

The graph is canonical; levels are views.

### Level 0

Project only universe/business/application/external boundary concepts and their major relationships.

### Level 1

Project major runtime architectural areas: frontend, API, backend, Agent, services/capabilities, Knowledge, Research, core infrastructure, persistence, external systems.

### Level 2

Project internal subsystem architecture. Agent internals must be separately discoverable, including session, reasoning, planning, execution, tools/orchestration, knowledge, memory, LLM, approval, audit, monitoring, avatar, interfaces, and verified related components.

### Level 3

Project exact repository implementation identity: package/module/file/class/function where evidence is available.

A node may appear at multiple levels. The level is a presentation projection, not a change of identity.

## 11. Bilingual search contract

The Explorer search index must index at least:

- `technical_name`
- `arabic_meaning`
- `arabic_description`
- `paths[]`
- `tags[]`
- important class/function names stored in `metadata`

English technical names remain exact. Arabic text is explanatory/searchable.

## 12. Validation rules

A graph dataset is valid only if all of the following hold:

1. Every node has a unique `id`.
2. Every edge has a unique `id`.
3. Every edge source and target exists in `nodes`.
4. Every node has at least one `evidence` reference unless it is explicitly marked `unverified`.
5. Every implemented node has at least one repository path or runtime-wiring evidence.
6. Every `planned_future` node/edge has governance or ADR evidence.
7. Every `reserved_minimal` node has evidence describing why it is reserved/minimal.
8. No edge silently connects two nodes using an inferred relationship without evidence.
9. `contains` edges represent structural hierarchy only.
10. `planned_migration_to` never represents current runtime flow.
11. `technical_name` must not be replaced by Arabic text.
12. Knowledge and Research must remain distinct node identities.
13. Tools and Business Services must remain distinct node identities where both are evidenced.
14. SQLite and PostgreSQL must not be represented as equivalent current runtime databases.
15. The dataset must not claim exhaustive repository coverage until a complete reconciliation pass has been completed.

## 13. Seed dataset policy

The first dataset built in Phase 1 is a **verified seed**, not the final exhaustive graph.

It must:

- cover the principal Level 0/1 architecture;
- expose the critical Agent path down toward Level 3;
- include Knowledge vs Research separation;
- include business capability/service distinction;
- include persistence/current-vs-future distinction;
- include cross-cutting concerns where evidence is already available;
- record evidence for every asserted relationship;
- explicitly identify what remains to be reconciled before the dataset can be called complete.

This prevents a small seed from being mistaken for the final architecture inventory.
