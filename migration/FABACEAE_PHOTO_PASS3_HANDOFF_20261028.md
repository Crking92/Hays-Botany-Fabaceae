# Fabaceae — Commons and GBIF photo migration handoff (28 October 2026)

**Private content/source-photo migration accounting is updated. Public website release and anatomy-arrow validation remain separate, unapproved gates.**

## Cumulative verified source-original inventory

| Checkpoint | Images physically archived | Species with at least one archived original |
|---|---:|---:|
| Original 200-image source inventory | 0 | 0 |
| Pass 1 (verified current iNaturalist + Commons) | 10 | 10 |
| Pass 2 (Commons URI/metadata, photo pixel retry) | 35 | 28 |
| **Pass 3 (exact current GBIF multimedia licenses, attribution, image pixels)** | **70** | **48 of 91** |

- **200/200 source image originals** have a disposition by exact source path, size, Git blob SHA and individual claim/decision.
- **70/200 originals are now physically archived in PRIVATE family staging** (35 new in GBIF pass 3), with matched metadata/licensing and SHA. **130 remain held in the unchanged original hub.**
- Latest Commons pass additionally verified 25 original photos, including **Desmanthus illinoensis** pods, **Senegalia greggii** curved thorns and **Vachellia constricta** pods.
- GBIF source pass checked 43 original photos; **35** had exact multimedia records with CC/CC0 image licenses, current creator/rightsHolder, matching taxon and perceptually matched source pixels. Eight remained held due missing/unsuitable exact multimedia rights or image matching.
- All 91 original species, 41 genera and 291 species/family/genus/source-credit metadata files remain staged with source continuity.
- **No image was transferred from an unverified source** just to improve percentage; no original hub photo was deleted or its public URL redirected.

## Remaining 130 original images, by first-pass hold reason

| Reason | Count |
|---|---:|
| Current photo rights noncommercial or not public-compatible | 46 |
| Other upstream platforms outside original first-pass checker (videos, linked websites, author media, etc.) | 39 |
| iNaturalist observation ID missing in old source metadata | 21 |
| Commons original file/API recheck failed; rights still need targeted confirmation | 11 |
| Commons license evidence not yet sufficient | 5 |
| Original file lacks unique, matching image-sources CSV record | 4 |
| Exact iNaturalist observation taxon did not match | 3 |
| Commons taxon filename needs human review | 1 |
| **Total original holds** | **130** |

The current Commons-specific recheck also surfaced explicit CC0/public-domain/CC BY-US licenses that lack a standard license URL. Those are *not automatically accepted* by the generic checker; leave held until exact-file provenance and underlying license basis are established.

## Field-first scientific and rights requirements still open

- The source/photo archive has verified original-image provenance, not diagnostic completeness. Several old source roles explicitly say “anatomy pending” or “provisional”; do not add anatomical arrows until structure is genuinely visible and placement manually reviewed.
- Generic/duplicate photos should not dominate the learner. Prefer fruits/pods, leaves, stipules, flowers, seeds, and thorns, with whole-plant reference limited where practical.
- Owner-provided Glass Root Garden / Calvin King photos belong in a separate exact-source, direct-author-permission lane. Do not re-label an all-rights-reserved or NC image as public CC merely because the user is the photographer.
- Particularly valuable next groups are 21 missing iNaturalist observation links, the seven identifiable owner photos, and the remaining 11 failed Commons technical checks.
- Preview/UI and native Glossary/Quiz routing still require working browser/production cutover QA; the original hub remains authoritative and independent Pages publishing is disabled.

## Source-of-truth audit files

- [Original 491-file census and immutable source hashes](fabaceae-pinned-source-file-ledger.json)
- [Every original photograph's current disposition](fabaceae-photo-200-decisions.json)
- [Verified photos with individual source, license and image evidence](fabaceae-verified-photo-ledger.json)
- [Cumulative GBIF-stage totals](fabaceae-photo-pass3-gbif-summary.json)
- [Read-only independent GBIF media comparison: all 43 decisions](fabaceae-gbif43-source-research.json)
- [Commons second-pass metadata and holds](fabaceae-commons-pass2-report.json)

**Deployment: NOT done. Raw family staging contains source/rights metadata and potentially non-public historical content. Do not turn the repository public, deploy new Pages or redirect the hub without final licensing/history/rollback checks and owner approval.**
