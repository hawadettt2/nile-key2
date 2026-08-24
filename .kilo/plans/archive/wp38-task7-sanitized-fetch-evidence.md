# Task 7 — Sanitized Fetch/Runtime Evidence

This document provides a sanitized sample of Moaah API request/response flow for verification purposes.

**Note:** No real API keys, tokens, or credentials are included in this document. All examples use simulated/test data.

## Request Flow

### 1. Adapter Query Entry Point

```python
# KnowledgeProviderRegistry.query("moaah", "steel pipes", context={"country": "840"})
# → MoaahExternalSourceAdapter.query("steel pipes", context={"country": "840"}, scope="keyword", limit=10)
```

### 2. Parameter Construction

```python
params = {
    "q": "steel pipes",
    "type": "keyword",
    "country": "840"
}
# Optional fields not present in this example:
# - affected_country
# - start_date
# - end_date
```

### 3. HTTP Request (Simulated)

```
GET https://mtech-api.com/client/api/regs-search?q=steel+pipes&type=keyword&country=840&token=***
Accept: application/json
```

**Sanitization:** The `token` parameter value is redacted. In production, this is loaded from `MOAAH_API_KEY` environment variable and is never logged or exposed in responses.

### 4. Mock Response (Test Data)

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
    ]
  }
}
```

### 5. Transformed Output

See `wp38-task7-transformation-example.md` for the full transformation result.

## Runtime Evidence

### Successful Query

| Attribute | Value |
|-----------|-------|
| Source ID | `moaah` |
| Query | `steel pipes` |
| Context country | `840` |
| Results returned | 1 |
| Confidence | 0.9 |
| Transformation time | ~3.44 ms (measured with mock client) |

### Graceful Degradation — Missing Country

| Attribute | Value |
|-----------|-------|
| Source ID | `moaah` |
| Query | `test` |
| Context country | *missing* |
| Results returned | 0 |
| Confidence | `null` |
| Behavior | Returns empty results immediately, no API call made |

### Graceful Degradation — Missing Credentials

| Attribute | Value |
|-----------|-------|
| Source ID | `moaah` |
| `base_url` | *empty* |
| `api_key` | *empty* |
| Registration | Skipped at startup |
| Query behavior | Returns empty results |

## Credential Handling Evidence

- `MOAAH_API_KEY` is loaded from environment variable via `config.py`
- Passed as query parameter `token` in HTTP request (Moaah API design)
- Never logged by adapter code
- Never returned in query response
- Never stored in transformed metadata
- Only referenced in `config.py` and `main.py` bootstrap

## No Raw Response Leakage

The adapter layer (`mooadapter.py`) never returns raw Moaah API responses. All outputs are transformed into the DEM knowledge shape before being returned to callers.
