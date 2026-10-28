# Fabaceae — first exact-source photograph migration and rights audit

**Date:** October 28, 2026  
**Status:** Verified source migration complete for first 10 photographs; 190 image holds are documented. Private staging only; **NOT** publication or completed photographic anatomy review.

## Baseline and current result

- **91 species, 41 genera** in the original Fabaceae source collection.
- **291/291 text and provenance files** were previously staged byte-identically; main original repository remains canonical.
- **200/200 original image files** included in the source ledger with exact original Git blob SHA and per-image audit decision.
- **10 images physically archived and SHA-verified** in private Fabaceae staging. All ten have traceable contemporary image-source evidence, compatible CC/CC0 permissions, exact image-pixel match and checked taxon association in the first pass.
- **10 of 91 species** have at least one of these vetted archived originals. This is **not 10 of 91 fully illustrated diagnostic lessons**.
- **190 original photographs** intentionally remain in the original hub, with individual documented reasons.
- No raw-source file was deleted, no visibility was changed, no main hub route was edited, and no new Pages publication occurred.

## What passed first-pass source checks?

| Taxon | Exact source class |
|---|---|
| Dalea candida | Wikimedia Commons / CC0 |
| Dalea compacta | Wikimedia Commons / CC0 |
| Desmodium paniculatum | iNaturalist / CC BY |
| Galactia canescens | iNaturalist / CC BY |
| Hylodesmum nudiflorum | iNaturalist / CC BY-SA |
| Kummerowia striata | iNaturalist / CC BY |
| Lespedeza texana | iNaturalist / CC BY |
| Neltuma glandulosa | Wikimedia Commons / CC BY |
| Pediomelum linearifolium | iNaturalist / CC BY |
| Pediomelum tenuiflorum | iNaturalist / CC BY |

**Note:** Exact numbers by evidence: 7 iNaturalist observation-photo confirmations and 3 Wikimedia Commons imageinfo confirmations. The group descriptions above use the original source class informally; rely on [the verified media ledger](fabaceae-verified-photo-ledger.json) for exact attribution and per-photo provenance, not this table.

## All 190 holds by first-pass reason

| Reason | Photo files |
|---|---:|
| Source platform beyond first-pass verification (GBIF, video, other) | 74 |
| Current photo license not public-compatible (typically NC) | 46 |
| Commons image API check encountered an HTTP failure | 25 |
| Exact iNaturalist observation ID missing | 21 |
| Current Commons metadata license not yet proven eligible | 16 |
| No unique matching `image-sources.csv` record | 4 |
| iNaturalist observation taxon does not match exact target | 3 |
| Commons filename taxon association needs human review | 1 |
| **Total held** | **190** |

Automated errors are **not evidence of infringement**, and a file's old `CC BY` claim is **not proof that its current licence was confirmed**. Preserve all held images and pursue alternative current-source verification when worthwhile. Do not silently promote a photo just to improve percentages.

## Next high-yield recovery order

1. Diagnose 25 Commons image API errors (e.g. request failure vs unavailable file) and 16 current-license holds from the exact Commons source pages, with pixel confirmation, credit, license terms and allowed modifications.
2. Review the 74 alternate-platform photos separately; prioritize original iNaturalist photo IDs or independently attributed GBIF multimedia, not generic library credits.
3. Audit 21 missing observation-ID cases; avoid blindly accepting provisional author/Joey photos and distinguish NC rights from public-compatible licenses.
4. Build a field-first gallery from actual verified originals and show license links; no fabricated arrows. Then backfill missing pods, thorns, leaves and reproductive macros rather than duplicate distant plants.

**Release gate remains blocked:** private staging may contain restricted source metadata; verify repository history, source rights, public site assets, real browser QA, routing and rollback before any independent family website cutover.

This is a maintainable rights/provenance backlog, not a declaration that all original photos have been moved or made public.
