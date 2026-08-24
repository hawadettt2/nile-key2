# Task 7 — Transformation Example

This document provides a concrete before/after example of Moaah API response transformation into the DEM `KnowledgeProvider` contract shape.

## Source: Moaah `/regs-search` Raw Response (Simulated)

```json
{
  "antidumping": {
    "antidumping_investigations": [
      {
        "uuid": "inv-1",
        "subject_product": "Steel pipes",
        "duty_measure_detail": "Affirmative | Measure applied",
        "publication_date": "2025-03-25",
        "id_link": "https://example.com/inv-1",
        "country": "840"
      }
    ],
    "antidumping_measures": [],
    "countervailing_investigations": [],
    "countervailing_measures": []
  },
  "importLicensing": [],
  "qr": {
    "data": [],
    "dataOrigin": []
  },
  "matched_hs_codes": []
}
```

## After Transformation — DEM Knowledge Shape

```json
{
  "id": "inv-1",
  "content": "Steel pipes - Affirmative | Measure applied",
  "source_id": "moaah",
  "confidence": 0.9,
  "metadata": {
    "section": "antidumping",
    "effective_date": "2025-03-25",
    "source_url": "https://example.com/inv-1",
    "country": "840",
    "hs_code": null,
    "regulation_type": "antidumping",
    "category": null,
    "version": "1.0.0",
    "fetch_timestamp": "2026-08-12T00:00:00Z",
    "record_hash": "computed-at-transform-time",
    "retrieval_status": "success"
  }
}
```

## Transformation Rules Applied

| Field | Rule |
|-------|------|
| `id` | `entry["uuid"]` → `"inv-1"` |
| `content` | `title + " - " + body` → `"Steel pipes - Affirmative \| Measure applied"` |
| `source_id` | Adapter config → `"moaah"` |
| `confidence` | `effective_date` present → `0.9` |
| `metadata.section` | Section key → `"antidumping"` |
| `metadata.effective_date` | `publication_date` → `"2025-03-25"` |
| `metadata.source_url` | `id_link` → `"https://example.com/inv-1"` |
| `metadata.country` | Direct → `"840"` |
| `metadata.hs_code` | Not present → `null` |
| `metadata.regulation_type` | Section fallback → `"antidumping"` |
| `metadata.category` | Not present → `null` |
| `metadata.version` | Adapter config → `"1.0.0"` |
| `metadata.fetch_timestamp` | Adapter config `updated_at` → `"2026-08-12T00:00:00Z"` |
| `metadata.record_hash` | Computed hash of entry items |
| `metadata.retrieval_status` | Constant → `"success"` |

## Confidence Rule Demonstration

| Condition | Value |
|-----------|-------|
| Base (no source_url, no effective_date) | 0.75 |
| `source_url` present | 0.85 |
| `effective_date` present | 0.90 |

In this example, `effective_date` is present (`"2025-03-25"`), so confidence = **0.9**.
