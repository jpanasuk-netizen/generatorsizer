# Lead form — fields & operator requirements (STAGED, front-end only)

Status: draft. `index.html#proLeadForm` renders name / ZIP / phone, intercepts
submit in `assets/monetization.js`, shows a local confirmation, and posts
NOWHERE. No endpoint, no storage, no email. Do not wire a backend until
Jeremy approves an operator deal in writing.

## Fields (front-end draft)

| Field | Input | Validation (on activation) |
|---|---|---|
| Name | text, maxlength 80, `autocomplete="name"` | required, trim, 2–80 chars |
| ZIP code | text, inputmode numeric, maxlength 10, `autocomplete="postal-code"` | required, `^\d{5}(-\d{4})?$` |
| Phone | tel, maxlength 20, `autocomplete="tel"` | required, 10+ digits after stripping non-digits |
| sized_kw (hidden) | `leadContext`, filled from calculator result when available | optional context for the operator |

No email field by design — phone is the installer's contact path. No consent
checkbox yet; add one at activation alongside the TCPA language counsel approves.

## What the operator deal must define (needs Jeremy's yes)

1. **Who receives leads** — named operator(s), coverage ZIPs, exclusivity per
   market or round-robin. No lead is shared with anyone until this is signed.
2. **Contact terms** — speed-to-lead SLA, max attempts, opt-out handling,
   TCPA compliance owner (operator must warrant compliant dialing/texting).
3. **Money** — per-lead fee vs per-booked-job vs revenue share; validation
   rules (bad ZIP, unreachable, duplicate); invoicing cadence.
4. **Data handling** — retention window, deletion on request, no resale clause,
   breach notice. Privacy page must be updated to name the operator before go-live.
5. **Quality gate** — licensed + insured verification, review-score floor,
   removal process after complaints.

## Activation checklist (after terms signed)

- [ ] Add endpoint: form `action` + server-side validation mirroring the table
- [ ] Add explicit consent checkbox + TCPA text
- [ ] Update `privacy.html` with operator name + data flow
- [ ] Change form tag from "Draft — not live" to live copy
- [ ] Log first 10 submissions end-to-end before announcing
