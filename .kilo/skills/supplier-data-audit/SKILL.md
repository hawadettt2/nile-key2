---
name: supplier-data-audit
description: >-
  Audit the suppliers dataset against its Excel source: extract the sheet,
  extract the database, compare field by field, and report exact serials that
  differ. Use when supplier records must be reconciled, a serial is missing or
  duplicated, or an import must be proven correct before and after a change.
---

# Supplier Data Audit

Reconciles two sources — the Excel workbook and the live `suppliers` table —
and reports differences by `source_serial`.

Every command below is the pattern already present in this repository. Scripts
are at the repository root; run them from there.

## Pipeline

```
Excel (.xlsx) → EXCEL_PARSED.json → EXCEL_BY_SERIAL.json ┐
                                                          ├→ compare → mismatches by serial
Database    → DB_RECORDS.json     → (keyed by serial) ────┘
```

## Step 1 — Extract the workbook

Two extractors exist. Use `read_excel.py` when `openpyxl` is available; it
preserves row order and blanks and locates the header row itself
(`read_excel.py:23-32`).

```bash
python read_excel.py
```

Output: `EXCEL_READED.json` with `all_rows`, `header_idx`, `header`.

If `openpyxl` is unavailable, `parse_excel.py` reads the sheet XML directly from
the `.xlsx` ZIP and decodes numeric entities (`parse_excel.py:14-21`):

```bash
python parse_excel.py
```

Output: `EXCEL_PARSED.json`.

Both scripts locate the target workbook by globbing `F:\nilekey\*\*.xlsx` and
matching `"162"` in the filename (`read_excel.py:3-8`). That glob is
machine-specific. On another machine, pass the real path instead of assuming the
pattern resolves.

## Step 2 — Key the Excel rows by serial

`build_excel_map.py` drops the header row and keys the remainder by column 0:

```bash
python build_excel_map.py
```

Output: `EXCEL_BY_SERIAL.json` — `{ "<serial>": {name, activity, address, phone, notes} }`.

It prints the record count, the serial range, and which serials are missing from
the expected range (`build_excel_map.py:23-25`). Read that line before comparing.

## Step 3 — Extract the database

`dump_db.py` copies a query into the backend container and writes the result:

```bash
python dump_db.py
```

Output: `DB_RECORDS.json` — a list of records with `id`, `source_serial`, `name`,
`activity`, `address`, `phone`, `notes`, `facility_type`, `parent_company_id`
(`dump_db.py:7-8`).

The container path `/app/data/nile_key.db` and container name
`nile-key22-backend-1` are hard-coded in that script (`dump_db.py:6,19-20`).
Confirm both before trusting the output.

## Step 4 — Compare field by field

```bash
python compare.py
```

`compare.py` builds a serial-keyed map of the database, then reports:

- serials present in Excel but not in the database
- serials present in the database but not in Excel
- per-field mismatches for serials present in both
- a count of fully matched records

Comparison normalizes `None` to `""` and trims whitespace before comparing
(`compare.py:24-27`), and checks `name`, `activity`, `address`, `phone`, `notes`
(`compare.py:37-46`). A mismatch is only reported when the normalized values
differ — so whitespace-only differences are invisible by design.

For a wider comparison that also covers serials missing from one side,
`compare_full.py` reads `EXCEL_PARSED.json` directly and accepts any row whose
first cell is numeric (`compare_full.py:8-12`).

## Step 5 — Check the specific serials that matter

`check_serial153.py` answers targeted questions against `EXCEL_READED.json`:

- is a given serial present in the data rows
- which serials are `None`
- every non-empty `notes` value
- the full record for a named serial, with `repr()` on `phone` and `notes`

```bash
python check_serial153.py
```

Use `repr()` on any field whose value is in question — it exposes stray
whitespace, non-breaking spaces, and escape artifacts that a printed value hides.

## Step 6 — Query the database directly for row-level checks

`audit1.py` runs a multi-question SQL script inside the container and returns one
JSON object: totals, counts with a serial, facility-type distribution, duplicate
serials, orphan accreditations, and duplicate accreditations per
supplier+source (`audit1.py:8-56`).

```bash
python audit1.py
```

`audit3.py` answers the narrower question of which suppliers have no
accreditation record, split by an Arabic keyword in `activity`
(`audit3.py:3-9`).

```bash
python audit3.py
```

## Reporting

Report findings as a table keyed by `source_serial`, one row per differing
serial, with the field, the Excel value, the database value, and which database
was queried. State the record counts on both sides — a comparison is only
meaningful if the reader knows the denominators.

## Boundaries

- Read-only against the database. This skill audits; it does not import or repair.
- Always name the database that was queried (host `backend/nile_key.db` vs
  container `/app/data/nile_key.db`). They are different stores.
- Never claim a field matches when only one side was read.
- `docker compose down -v` destroys the `db-data` volume — never run it during an
  audit.