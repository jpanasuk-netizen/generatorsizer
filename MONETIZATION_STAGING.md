# Monetization — LIVE 2026-09-10: Layer 1 (Amazon tag generatorsi0d-20) + AdSense auto-ads (ca-pub-1045858506533973) live. Layers 3-4 still inert.

Branch state: uncommitted working-tree edits on `master`, NOT pushed.
Evidence: `git status --short` + `git diff --stat` in the site folder.
Rule: nothing here earns or collects anything until Jeremy supplies the
item listed per layer. No income claims appear in any on-page copy.

## Layer 1 — Affiliate slots (Amazon search templates, no Associate ID)

- What: `[data-amz]` search links under calculator results + all article slots
  (`index.html` gen tab + transfer-switch tab, `best-portable-generators.html`
  slots 1–10, fridge / well-pump / commercial-service pages).
- Swap point: single constant `AMAZON_TAG` in `assets/monetization.js`.
  While it reads `YOUR-ASSOCIATE-ID-20`, links render as plain Amazon search
  URLs with `rel="sponsored nofollow noopener"` and zero tracking.
- Staged note (`data-amz-staged-note`) is shown to readers until activation.
- **Jeremy must supply: Amazon Associate ID** (after Associates approval +
  3 qualifying sales stick). Then: set tag, hide staged notes, confirm the
  rankings-page disclosure stays.

## Layer 2 — AdSense slots (responsive placeholders, no publisher ID)

- What: `.adsense-slot` placeholder divs (`index.html`, rankings page,
  3 articles). The `<ins>` unit + loader script are COMMENTED OUT — no ad
  network request fires, no profiling.
- **Jeremy must supply: AdSense publisher ID** (`ca-pub-…`) + ad-slot IDs.
  Then: replace placeholders, uncomment loader, name the network in
  `privacy.html` ("Advertising (staged)" section is pre-written for this).

## Layer 3 — Lead form draft (front-end only, posts nowhere)

- What: `index.html#proLeadForm` — name / ZIP / phone + hidden sized-kW
  context. Submit is intercepted, nothing leaves the browser.
- Spec: `lead-form-fields.md` (validation table + operator requirements).
- **Jeremy must supply: operator terms** — named receiving operator, coverage,
  contact/TCPA terms, payout model, data-handling + no-resale, quality gate.
  Then run the activation checklist in `lead-form-fields.md` (endpoint,
  consent checkbox, privacy update) before going live.

## Layer 4 — Whop sizing-report outline (spec only, no product)

- What: `whop-sizing-report.md` — report outline, fulfillment sketch,
  activation checklist. No Whop product exists; the site carries only an HTML
  comment placeholder, no offer, no price, no buy link.
- **Jeremy must supply: the Whop pick** — product + price, delivery SLA,
  placement, copy gate. Then build the upsell card per the checklist.

## Files changed (this staging)

- `index.html` — layer 1 links, layer 2 slot, layer 3 form, Whop comment
- `best-portable-generators.html` — 10 slot links, layer 2 slot, disclosure line
- `refrigerator-freezer.html`, `well-pump-watts.html`,
  `find-a-commercial-generator-service.html` — slot links + layer 2 slot
- `privacy.html` — staged-state disclosures (affiliate / ads / lead form)
- `assets/styles.css` — `.btn-amz`, `.adsense-slot`, `.lead-form` (mobile-first)
- `assets/monetization.js` — NEW: tag swap point + lead-form intercept
- `lead-form-fields.md` — NEW: layer 3 spec
- `whop-sizing-report.md` — NEW: layer 4 spec

## Verify before push (run in site folder)

- `git status --short` shows edits uncommitted, `git log origin/master..HEAD`
  empty (nothing pushed)
- `grep -riE "ca-pub-[0-9]|tag=[A-Z0-9-]+-20|adsbygoogle\.js" --include="*.html" .`
  returns only `YOUR-` placeholders / commented lines
- `node --check assets/monetization.js`
- `grep -riE "earn \$|make money|passive income|guaranteed" --include="*.html" --include="*.md" .` empty
