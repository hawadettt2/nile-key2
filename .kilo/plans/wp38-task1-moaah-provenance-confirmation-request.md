To: contact@moaah.com
Subject: WP-38a Integration Evaluation — Public API Provenance Fields Confirmation Required

Dear Moaah Team,

We are evaluating Moaah Public API as a candidate provider for our Knowledge Ingestion pipeline. Before proceeding to approval, we need formal written confirmation on the following items related to record-level provenance in the public API.

Questions

1. Record-level provenance in /regs-search
   For each regulatory record returned by /regs-search, does the public API return provenance fields at the record level? Specifically:
   - source_url
   - source_authority
   - effective_date
   - legal_act_reference
   
   If yes, please confirm the exact field names as they appear in the API response.

2. Committed timeline if provenance is not currently available
   If these fields are not currently available in the public API, is there a committed timeline to add them? Please provide an estimated availability date or milestone if possible.

3. Actual API response sample for Egypt
   Please provide an actual API response sample for Egypt (country code 818) showing the full record structure returned by /regs-search or related regulatory endpoints. This will help us verify data completeness and field coverage for our target market.

Context
- We are bound by a knowledge ingestion contract that requires traceability and evidence metadata at the record level.
- We have reviewed the public OpenAPI schema at https://mtech-api.com/client/api/schema and did not find these provenance fields documented for regulatory endpoints.
- Your web interface mentions "Administration Information (source of legal act and ruling)"; we need to confirm whether this information is exposed via the public API.

Please reply to this email with your written confirmation at your earliest convenience.

Best regards,
Nile Key DEM Team
Date: 2026-08-11
