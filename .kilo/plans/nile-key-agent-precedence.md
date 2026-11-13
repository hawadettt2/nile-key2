# Nile Key — Agent Precedence & Registry

**Version:** 1.0
**Kilo version verified:** 7.4.21
**Verification method:** live `kilo.exe debug config` / `kilo.exe debug agent <name>` against this repository, plus a throwaway sandbox under `%TEMP%` for merge and precedence tests (since removed).

Everything in this document was proven by running Kilo. Nothing here is inferred from documentation alone.

---

## 1. Verified Precedence Rules

### 1.1 Agent merge is deep, not replacement — PROVEN

Test: sandbox with `kilo.json` defining `agent."forensic-audit"` and a separate `.kilo/agent/forensic-audit.md`.

| Source | `description` | `permission` |
|---|---|---|
| `kilo.json` (project) | `FROM_ROOT_KILO_JSON` | `bash: deny` |
| `.kilo/agent/forensic-audit.md` | `FROM_DOT_KILO_AGENT_MD` | *(absent)* |

Resolved result:

```
prompt       = "PROMPT_FROM_MD"
description  = "FROM_DOT_KILO_AGENT_MD"
permission   = { "bash": "deny" }      <-- inherited from kilo.json
```

**Conclusion:** the agent is the deep merge of both sources. Fields present in the `.md` file win; fields absent from it are inherited from config.

### 1.2 `.kilo/agent/*.md` beats `kilo.json` for the same field — PROVEN

Test: both sources set `permission.bash`.

| Source | `permission.bash` |
|---|---|
| `kilo.json` | `deny` |
| `.kilo/agent/forensic-audit.md` | `allow` |

Resolved result:

```
permission = { "bash": "allow", "edit": "deny" }
```

**Conclusion:** for a field defined in both, the `.md` file wins. Project `kilo.json` is not the final word on any field an agent file also defines.

### 1.3 Permission objects deep-merge across config layers — PROVEN

Test: global config has `external_directory: { "C:\\Users\\OSAMA\\erpnext-docker\\*": "allow", "*": "allow" }`; project `kilo.json` sets `external_directory: { "*": "ask" }`.

Resolved result:

```
{
  "C:\\Users\\OSAMA\\erpnext-docker\\*": "allow",   <-- preserved from global
  "*": "ask"                                        <-- overridden by project
}
```

**Conclusion:** permission objects merge per-key. A project override replaces only the keys it names.

### 1.4 Permission rules: LAST match wins, not first — PROVEN

Test: sandbox `kilo.json` with `bash: { "*": "ask", "git status": "allow" }` — broad rule **first**, specific rule **last**. Then reversed.

Ran `kilo run` with `--print-logs` and read the evaluated decision:

| Rule order | Decision for `git status` |
|---|---|
| `*: ask` then `git status: allow` | `action=allow source=project` |
| `git status: allow` then `*: ask` | `action=ask source=project` (auto-rejected) |

**Conclusion:** the **last** matching rule wins. This is the opposite of what some documentation implies, and it is the single most important rule for authoring permissions.

### 1.5 Project config loads after global, so global rules can override project intent — PROVEN

Resolved `external_directory` list for agent `code` (ordered) after the project set `external_directory: { "*": "ask" }`:

```
1. ask   <- *
...      (agent-level allow rules)
11. ask  <- *                              <-- project block
...
21. allow <- C:\Users\OSAMA\erpnext-docker\*
22. ask  <- *                              <-- project block (again)
23. allow <- C:\Users\OSAMA\erpnext-docker\*
24. ask  <- *                              <-- project block (again)
25. allow <- C:\Users\OSAMA\.local\share\kilo\tool-output\*
```

Because global `external_directory: { "*": "allow" }` resolves **after** the project block, and last-match-wins, the project's attempt to narrow `external_directory` is **defeated** by the global `*: allow`.

**Conclusion:** a project-level `external_directory` restriction cannot tighten access while the global config ends with `"*": "allow"`. Fixing that requires editing global config — out of scope for a shared project file.

---

## 2. Why the Plan's Proposed Global Permission Block Was Not Adopted

The governance plan proposed a shared `permission` block in the root `kilo.json`. It was tested against every agent **before** adoption, and rejected on evidence.

### 2.1 It breaks the built-in `code` agent

| Agent | Before | After proposed block |
|---|---|---|
| `code` | `bash=allow` `edit=allow` | **`bash=ask` `edit=ask`** |
| `forensic-audit` | `bash=allow` `edit=allow` | `bash=ask` `edit=ask` |
| `incident-remediation` | `bash=allow` `edit=allow` | `bash=ask` `edit=ask` |
| `data` | `bash=allow` `edit=allow` | `bash=ask` `edit=ask` |
| `general` | `bash=allow` `edit=allow` | `bash=ask` `edit=ask` |
| `architect` | `bash=deny` `edit=allow` | `bash=deny` `edit=allow` (own override) |

Turning `bash` and `edit` to `ask` for every agent would force an approval prompt on every command and every edit in normal work. That is a functional regression, not a security improvement.

### 2.2 Its `external_directory` restriction does not take effect

Proven in 1.5: the global `"*": "allow"` resolves after the project block and wins under last-match-wins. The proposed `external_directory: { "*": "ask" }` would have added noise without changing behaviour.

### 2.3 Decision

**No `permission` block was added to the root `kilo.json`.** Permissions were set per agent instead, where they are precise and provably do not affect other agents (see 3.2).

---

## 3. Agent Registry

### 3.1 Project agents (`.kilo/agent/*.md`) — canonical for Nile Key

| Agent | Mode | Source | Proven permissions | Approver |
|---|---|---|---|---|
| `forensic-audit` | `primary` | `.kilo/agent/forensic-audit.md` | `edit: deny`, `task: deny` | Project owner |
| `incident-remediation` | `primary` | `.kilo/agent/incident-remediation.md` | `edit: ask`, `task: deny` | Project owner |

Both are tracked in Git. Both also exist inline in the global config; the project `.md` files are canonical here and win on any shared field (proven 1.2).

### 3.2 Verified effect on other agents

After adding the per-agent permissions above, all other agents are unchanged:

| Agent | `bash` | `edit` | `task` |
|---|---|---|---|
| `code` (built-in) | allow | allow | *(unset)* |
| `forensic-audit` | allow | **deny** | **deny** |
| `incident-remediation` | allow | **ask** | **deny** |
| `architect` (global) | deny | allow | *(unset)* |
| `data` (global) | allow | allow | *(unset)* |
| `general` (built-in) | allow | allow | *(unset)* |

Only the two project agents changed. No global or built-in agent was affected.

### 3.3 Global agents (read-only — not modified)

| Agent | Source |
|---|---|
| `test-engineer` | `~/.config/kilo/agents/test-engineer.md` + inline |
| `frontend-specialist` | `~/.config/kilo/agents/frontend-specialist.md` + inline |
| `data` | `~/.config/kilo/agents/data.md` + inline |
| `architect` | `~/.config/kilo/agents/architect.md` + inline |
| `incident-remediation` | inline in `~/.config/kilo/kilo.jsonc` |
| `forensic-audit` | inline in `~/.config/kilo/kilo.jsonc` |

`~/.config/kilo/kilo.jsonc` SHA-256 was identical before and after this phase:
`C6E5460EE996384B27883885C006DAB11305AEB96A0192C576122D6B97CD7072`

### 3.4 `.kilo/agents/` (plural) — does not exist, must not be created

Kilo scans both `{agent,agents}/**/*.md`. Creating `.kilo/agents/` would create a second source for the same agents and reintroduce the ambiguity this phase removes. `.kilo/agent/` (singular) is the single canonical project location.

---

## 4. Adoption Gate

No agent may be added or modified unless it has:

1. `description` in frontmatter
2. `mode` in frontmatter
3. Explicit `permission` if it should differ from the inherited default
4. A row in the registry above
5. Documented project-owner approval

## 5. Commands to Re-verify

```powershell
$kilo = "C:\Users\OSAMA\.vscode\extensions\kilocode.kilo-code-7.4.21-win32-x64\bin\kilo.exe"

# resolved config, including instruction and agent merge
& $kilo debug config

# one agent's fully resolved permission list
& $kilo debug agent code

# skills actually discovered
& $kilo debug skill
```