# Nile Key Engineering System

The `.kilocode` directory is the engineering operating system of the Nile Key project, containing all rules, workflows, and state required for consistent development.

## File Map

**00_README.md** - Entry point and navigation guide for the engineering system.

↓

**NILE_KEY_RULES.md** - Architecture constitution defining project principles and policies.

↓

**PATCH_WORKFLOW.md** - Mandatory execution lifecycle for every patch.

↓

**SESSION_STATE.md** - Historical work-package record. **STOPPED** - not a source of current project state (last recorded package: WP-10). See "State Authority" below.

↓

**04_KILO_SETUP.md** - Historical environment snapshot. Verify against the live config before use.

Always start here before working on the project.

## How Rules Are Loaded (Kilo 7.4.21)

Rules are wired to Kilo through the `instructions` array in **`kilo.json`** at the repository root (tracked, shared with the team):

```json
{
  "$schema": "https://app.kilo.ai/config.json",
  "instructions": [
    ".kilocode/NILE_KEY_RULES.md",
    ".kilocode/PATCH_WORKFLOW.md"
  ]
}
```

Instruction sources, highest priority first:

| Priority | Source | Location |
|---|---|---|
| 1 | Per-agent prompt | `agent.<name>.prompt` |
| 2 | `instructions` | `kilo.json` (repository root) |
| 3 | `AGENTS.md` | repository root (write-protected) |
| 4 | `instructions` | `~/.config/kilo/kilo.jsonc` |
| 5 | Skills | `.kilo/skills/` (loaded on demand) |

Verify what Kilo actually resolved:

```powershell
& "<kilo.exe>" debug config
```

## Config Ownership

| File | Tracked in Git | Purpose |
|---|---|---|
| `kilo.json` (root) | Yes | Shared project config: `instructions`, `permission` |
| `.kilo/kilo.jsonc` | **No** - ignored by `.gitignore:32` | Machine-local only. Never rely on it for shared settings. |
| `~/.config/kilo/kilo.jsonc` | No (user profile) | Global personal config |
| `AGENTS.md` | Yes | Project instructions. Write-protected - edits require explicit user approval. |

## State Authority

- **`CURRENT_STATUS.md`** is an index, not the final authority. It declares its own authority as `.kilo/plans/1789672443844-master-remediation-plan.md` + `.kilo/plans/1789733769109-commercial-readiness-completion.md`.
- `PLAN.md` and `CURRENT_STATUS.md` disagree on current phase. That conflict is tracked as open item **D9** in `.kilo/plans/nile-key-agent-governance-plan.md` and must be resolved by the project owner.
- **`.kilocode/SESSION_STATE.md` is stopped and must not be used as a state reference.**
- Never commit unless the project owner explicitly asks.