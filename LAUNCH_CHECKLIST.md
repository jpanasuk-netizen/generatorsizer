# GeneratorSizer.com — Launch Checklist

Site files: `HermesVault/40-Content/sites/generatorsizer/`
Source asset it expands: `github.com/jpanasuk-netizen/battery-bank-sizer` (live generator-sizing-calculator.html stays as the bridge page).

## 0. Pre-launch (before anything public)
- [ ] Jeremy approves publish (charter human gate — no live URL without his yes)
- [ ] Pick hosting path (recommend A) and set the final domain in: sitemap.xml, robots.txt, and each page's canonical + og:url (search `generatorsizer.com` across files)
- [ ] Verify wattage figures against current manufacturer spec sheets (figures are 2026-typical published values)
- [ ] Decide affiliate monetization timing — apply to programs BEFORE adding real links; placeholder slots are marked `<!-- AFFILIATE SLOT -->` in index.html and all 3 articles

## 1. Hosting — GitHub Pages ($0)
- [ ] Create repo `jpanasuk-netizen/generatorsizer` (public), push the site folder contents to `main`
- [ ] Settings → Pages → Deploy from branch: `main` / root → confirm green URL `jpanasuk-netizen.github.io/generatorsizer/`
- [ ] If buying generatorsizer.com: registrar (Namecheap/Porkbun), then repo Settings → Pages → Custom domain → `generatorsizer.com`, DNS: A records for apex (185.199.108-111.153) + CNAME www → jpanasuk-netizen.github.io, enable "Enforce HTTPS"
- [ ] Mirror to Hugging Face Space `jpanasuk/generatorsizer` (sdk: static) as the twin — matches the existing packet-twin pattern

## 2. Search Console
- [ ] Verify `generatorsizer.com` via DNS TXT (or the github.io URL via HTML file)
- [ ] Submit `sitemap.xml`
- [ ] URL Inspection → Request indexing on all 4 pages
- [ ] Week 2: check Coverage + Performance; then submit to Bing Webmaster Tools (imports GSC property in 2 clicks)

## 3. Affiliate programs (apply in this order)
- [ ] **Amazon Associates** — generators/inverters/transfer switches; needs 3 qualifying sales in 180 days to stick. Build links only after approval; keep disclosure paragraph already on the rankings page
- [ ] **Electrician lead-gen options** (higher payouts than retail): check ServiceTitan-affiliate style programs, HomeAdvisor/Angi partner sign-up, or local electrician sponsorship banner for the transfer-switch article — pick ONE, needs Jeremy's yes on terms
- [ ] Later: AdSense once organic traffic exists (~20+ sessions/day)

## 4. Distribution (per NICHE_SITES_PLAN 2-engine model)
- [ ] r/preppers, r/OffGrid, r/Generator, generator forums: answer 2–3 sizing threads/week with genuinely useful replies; link the calculator only when it's actually the tool for the question
- [ ] Cross-link: add a "GeneratorSizer ↗" line to the battery-bank-sizer index + llms.txt AFTER this site is live (reciprocal, not orphan)
- [ ] Update battery-bank-sizer llms.txt "Coming pages" → point generator page at the new hub

## 5. Post-launch QA
- [ ] Test all 4 calculator tabs on a phone (mobile-first build; verify textarea + load-row grid at 375px)
- [ ] Rich Results Test: SoftwareApplication + FAQPage + ItemList validate
- [ ] Lighthouse mobile ≥ 95 perf (static site, single CSS/JS — should pass clean)
- [ ] Confirm no affiliate links ship before program approval (slots are placeholders by design)
