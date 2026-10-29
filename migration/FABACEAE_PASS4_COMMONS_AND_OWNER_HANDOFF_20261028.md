# Fabaceae — photo migration pass 4 handoff (October 28, 2026)

**Private staging only. Original Hays Botany hub remains canonical; no independent Pages publication or routing cutover.**

## Verified inventory
- 91/91 Fabaceae species records and 291/291 source scientific and provenance text files copied from the canonical, unchanged source tree.
- **82 of 200 original photos** now physically byte-verified in private staging; **118 original images held** with documented reasons.
- Of 82 archived originals, **75 have compatible current individual CC/CC0 or Commons/GBIF rights evidence**, and **7 belong to the original photographer and have separate project-specific private authorization**. The seven must **never** be counted as unrestricted public Creative Commons photographs.
- **54 of 91 species** have at least one archived original photograph; anatomy-photo quality and arrows are not certified.

## Five new Commons source originals
A stricter recheck of explicit CC0 and CC BY 3.0 US terms recovered five photos:
- Desmanthus acuminatus: two (whole-plant view and leaf/flower detail) — Btcpg, CC0
- Mimosa biuncifera: one — Daniel, CC0
- Vachellia farnesiana: one flower/leaf view — Forest and Kim Starr, CC BY 3.0 US
- Vicia ludoviciana: one — Patrick Alexander, CC0

Three other candidates failed original-versus-current photo pixel matching; no rights or species claims were guessed.

## All seven Glass Root Garden / Calvin King source photos recovered, separately restricted
Four already had observation IDs in their exact original source CSV. The other three were recovered from the official observation API by querying the verified owner's observations for exact matching photo ID and taxon, then confirming the pixel match.

| Species | Private-owner originals |
|---|---:|
| Dalea enneandra | 1 |
| Dalea neomexicana | 1 |
| Neltuma glandulosa | 2 |
| Rhynchosia minima | 1 |
| Rhynchosia senna | 1 |
| Sesbania drummondii | 1 |
| **Total** | **7** |

The original iNaturalist records retain their **all rights reserved** licenses. Existing direct-author permission supports the **private Hays Botany learner with attribution**, not an invented current CC grant or automatic commercial release. Private photo captions identify Glass Root Garden (Calvin King) and explicitly warn about those limits.

## Remaining 118 held original photos

| Reason still blocking automatic clearance | Count |
|---|---:|
| Noncommercial or otherwise incompatible public reuse terms | 42 |
| Other upstream source platform not independently checked | 39 |
| Missing exact iNaturalist observation linkage | 18 |
| Commons API/technical source check unresolved | 6 |
| Commons license basis not independently verified | 5 |
| No unique original photo-credit CSV row | 4 |
| iNaturalist taxon mismatch | 3 |
| Commons taxonomic filename needs review | 1 |
| **Total** | **118** |

The exploratory iNaturalist photo-page check returned HTTP 403 for 25 old photo pages; this was a website-access limitation, not evidence of bad rights. An observation-API fallback verified the seven owner originals; the remaining missing observation IDs are mostly noncommercial records that should stay on hold pending appropriate source evidence.

## Exact source-of-truth records
- [200 original-photo decisions](fabaceae-photo-200-decisions.json)
- [75 public-license-compatible original-photo records](fabaceae-verified-photo-ledger.json)
- [Seven private-owner-permission original-photo records](fabaceae-private-owner-photo-ledger.json)
- [Seven owner-source verification summary](fabaceae-owner-seven-private-archive-summary.json)
- [Commons strict license and pixel source checks](fabaceae-commons-explicit-cc0-us-pass4.json)
- [Blocked iNaturalist photo-page probe](fabaceae-inat25-readonly-source-audit.json)
- [Three recovered owner observation/photo links](fabaceae-owner-three-unlinked-evidence.json)

**Do not deploy Pages, change repo visibility, alter the public hub, or add anatomy arrows without separate validation.**
