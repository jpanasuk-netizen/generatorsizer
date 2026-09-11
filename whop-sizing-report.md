# Whop sizing report — product outline (SPEC ONLY, no product)

Status: one-pager spec. No Whop product created, no link on the site (only an
HTML comment placeholder in `index.html`). Nothing to buy, no prices promised
on-page, no income claims anywhere.

## Concept

A personalized PDF "Generator Sizing Report" for readers who ran the free
calculator and want a saveable, shareable plan: their loads, the math, the
wattage class to buy, fuel plan, and transfer-switch notes — generated from
the same published figures the site uses.

## Report outline (1–2 pages)

1. **Your loads** — appliance list with running + starting watts as entered
2. **The math** — running total, largest-motor surge adder, headroom %,
   recommended minimum running + surge watts
3. **Buy box** — wattage class (e.g. 4,500 W dual-fuel), 240 V yes/no,
   inverter vs conventional note, THD note for electronics
4. **Fuel plan** — tank hours at 50% load, gallons/day at stated hrs/day,
   gas vs propane storage note
5. **Install notes** — transfer-switch amperage match, permit/code reminder,
   "licensed electrician" pointer with link to the vetting checklist
6. **Disclaimer** — planning estimate, verify against spec sheets + local code

## Fulfillment sketch (to decide at build time)

- Option A: static checkout → email template → manual PDF within 48h
- Option B: client-side PDF generation (print-to-PDF stylesheet of results)
- Start with A; B removes fulfillment labor if volume justifies the build

## What Jeremy must pick (the Whop decision)

1. **Product + price** — create the Whop product, set the price, own refunds
2. **Delivery SLA** — manual turnaround promise or automated build
3. **Placement** — results-adjacent upsell card vs dedicated report page
4. **Copy gate** — no earnings/savings promises; "plan, not engineering sign-off"

## Activation checklist (after the pick)

- [ ] Whop product live → add upsell card under `#genResult` + report page link
- [ ] Fulfillment path tested with 3 sample inputs
- [ ] Refund + disclaimer copy reviewed
- [ ] `privacy.html` updated if buyer email is collected on-site
