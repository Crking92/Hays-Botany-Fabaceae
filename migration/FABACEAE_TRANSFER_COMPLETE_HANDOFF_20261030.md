# Fabaceae — SOURCE TRANSFER COMPLETE / ready for next family (October 30, 2026)

## Decision and scope

**Migration status: COMPLETE.** All original data and photographs have been transferred and are accounted for in the assigned Fabaceae repository. This closure is **about source-file preservation, routing, functional family website and existing-photograph placement**. It does **not** certify every plant's identification, every arrow or future photo coverage. The team can move to the next family without waiting for new photographs or new botanical data.

## Exact live repository audit (compared against original hub)

- Original source: `Crking92/Hays-County-Botany`, `main`; read-only legacy baseline.
- Destination: `Crking92/Hays-Botany-Fabaceae`, `staging/fabaceae-metadata` for botanical source; `main/site` for rights-filtered public learner.
- **491/491** original source files exist in the family staging repository at the same paths recorded by `migration/fabaceae-all-original-491-file-transfer-manifest.json`; no missing files.
- **487** source files are still **byte-for-byte identical** to the original main-repo versions.
- **4** transferred *species.json* files have only later intentionally revised photo credit/source metadata; these are *Dalea aurea*, *Dalea compacta*, *Dalea frutescens*, and *Senegalia wrightii*. Their original hub versions remain unchanged and source-file history is preserved.
- **91/91 species records** transferred. The other original files comprise 200 original photograph binaries and 200 other text/source-credit files (491 total).
- All **200/200 original photo binaries** remain in the family repository across preserved source/rights-hold paths. The original 200 remain in the legacy hub. No photos were discarded to improve the website's licensing score.
- The original source-card metadata also includes **18 external image URLs** (only links, with no preexisting archived local photo bytes). These are documented as **reference-only**, not lost photographs.
- All **91 species lessons** are available in the new family's public `site`, with **88 rights-filtered photo files across 59 species**. **32 species** have no eligible public gallery photograph yet.
- The [full live QA run](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/41063761970) fetched and validated all **91 cards** and compared all **88 displayed originals** byte-for-byte against the repository. The exact 75-entry previously vetted CC/CC0 image archive is **75/75** placed in the corresponding published species folders.
- In the current display filter, **130/218 original image metadata records** remain held for future photo permissions/source work: 110 rights/terms held; 18 external-link-only; 2 lacking adequate individual-photo proof. This is a display policy backlog, **not unfinished source transfer**.
- The 7 independently confirmed owner-authored originals have only private-study authorization in archived evidence; they remain preserved without inventing a public Creative Commons grant.
- No new external photos were collected in the recovery passes. No new botanical species records, anatomy data or illustrations added. No legacy hub source edits or automation restart.

## Four metadata changes vs unchanged hub

| Species | Why intentional change? |
|---|---|
| *Dalea aurea* | Resolve exact Commons creator attribution for one original photo |
| *Dalea compacta* | Resolve exact CC0/Commons photographer and credit |
| *Dalea frutescens* | Resolve exact Commons creator/license for archived shrub photo |
| *Senegalia wrightii* | Pin original CC BY guide photo to its individual photo ID |

These changes were made in `staging/fabaceae-metadata`. No original botanical narrative was overwritten for the purpose of migrating photo rights.

## What remains deferred

**Future enrichment, not a migration blocker:** add new species/photos/diagnostic closeups, individually review the 110 held-license records, decide which of the 18 external-only references deserve new archiving later, and perform botanical morphology/arrow QA. Never loosen the public filter to publish all-rights-reserved or ambiguous records.

**Routing and safeguards:** send all future Fabaceae editorial changes directly to `Crking92/Hays-Botany-Fabaceae` branch `staging/fabaceae-metadata`; published releases need their own authorization. Leave the original `Crking92/Hays-County-Botany` botanical library as a read-only fallback. Do not resume paused automations or perform any new image harvest as part of the cross-family migration.

**Next family collection:** Lamiales, `Crking92/Hays-Botany-Lamiales`, already has **102 assigned species**, **582 source files** (342 text/source and 240 original image binaries) staged in `staging/original-source-transfer`. Begin with an unchanged-source/website-index audit, not new collection.

Historical detailed files: [all-original source transfer manifest](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/fabaceae-all-original-491-file-transfer-manifest.json), [88-photo live QA and licensing history](FABACEAE_75_VETTED_ARCHIVE_COMPLETE_88_LIVE_QA_20261030.md), [source-only reference audit](FABACEAE_REMOTE_REFERENCE_AND_ARCHIVED_CC_BY_PASS_20261030.md).
