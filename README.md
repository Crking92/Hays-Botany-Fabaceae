> **OCTOBER 29 VERIFIED FABACEAE PHOTO RECOVERY (LATEST):** **31 of 91 species** display **44 source-credited photographs** in the [live Fabaceae Visual Learner](https://crking92.github.io/Hays-Botany-Fabaceae/site/). The [full deployed QA](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40937669131) passed all **91 species pages** and verified **44/44 live image URLs** against the original bytes. This is up from 13/20 at the start of the latest recovery: 18 species gained a first photo, and honey mesquite gained two more views. Two archived *Dalea* images had their original photographers independently verified against Commons and corrected in the family staging metadata. **60 species currently lack a public image** and **174 individual image metadata records remain held** for recorded reasons (149 unverified/restricted license, 18 remote/nonlocal originals, 5 insufficient photo-specific source proof, 2 public-reuse notes not yet cleared). No new photos were harvested; all original image bytes and the read-only historical hub were preserved. This updates the historical figures below. Detailed [source/photo audit](migration/FABACEAE_SOURCE_AND_GALLERY_QA_CHECKPOINT_20261029.md).

> **CURRENT FAMILY SOURCE/WEBSITE AUDIT — October 29, 2026:** This repository is **PUBLIC** with an active [Fabaceae Visual Learner](https://crking92.github.io/Hays-Botany-Fabaceae/site/). All **91** species lessons are present. **18 source-credited original photographs across 11 species** display successfully; the [live photo QA run](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40934030037) confirmed all 18 hosted files are byte-for-byte identical to the published originals. 80 species have no released photo and 200 historical image metadata records remain held in the rights-gated gallery (distinct from the 200 original image files in the historical 491-file migration). Original source transfer was previously verified as **491/491**, but this audit did not redo all those source hashes. See [Fabaceae source and photo QA checkpoint](migration/FABACEAE_SOURCE_AND_GALLERY_QA_CHECKPOINT_20261029.md). Historical text below that calls the now-public staging branch 'private' is superseded. No new images harvested or paused automations restarted.

# Hays Botany — Fabaceae

**Status: all 491 original source files transferred into private staging; separate media rights/publication release still held.**

The Asteraceae private content/photo handoff is complete enough to progress to Fabaceae while the original [Hays County Botany learner](https://github.com/Crking92/Hays-County-Botany) remains the authoritative botanical source and public website.

## Complete existing-file transfer — verified

**491/491 original Fabaceae files are now physically present and source-Git-hash checked in [private staging](https://github.com/Crking92/Hays-Botany-Fabaceae/tree/staging/fabaceae-metadata): 291 scientific/source-credit text files and all 200 original photographs.** Of those original photographs, 82 remain in the source-verified private learner gallery and 118 are byte-identical copies in a separate private **non-displayed** rights-hold archive.

[Full original file verification](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/fabaceae-original-migration-completion-summary.json) · [491-file destination-by-destination manifest](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/fabaceae-all-original-491-file-transfer-manifest.json)

This finishes *original source-file transfer*, not photo licensing or public release. The original Hays Botany hub remains authoritative; eighteen references to external image URLs remain preserved as links, not downloaded photos.


## Verified initial staging — October 28, 2026

- **91 of 91 species cards** copied to [private Fabaceae staging](https://github.com/Crking92/Hays-Botany-Fabaceae/tree/staging/fabaceae-metadata).
- **291 of 291 scientific, genus/family and photo-credit metadata files** byte-verified against original Git blobs.
- **200 of 200 source originals** individually reconciled; **82 originals physically archived in private staging** after exact current-source, image-pixel, creator and CC/CC0 rights checks. **118 originals remain held** with specific reasons in the original hub. This is not a public Pages release.
- Canonical Fabaceae Git source tree is unchanged: `947ac940c97f273db03e7b42f5dc992241871527`.
- New family index is populated for offline data validation but stays `STAGING_ONLY`. No hub route, project rules, public Pages, original source files or family ownership changed.

[Successful text-only staging workflow](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40785958622) · [Machine-readable staging audit](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/fabaceae-text-only-stage-summary.json) · [Original 491-file source ledger](migration/fabaceae-pinned-source-file-ledger.json)

[Fabaceae first-photo-rights audit and exact hold counts](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/FABACEAE_FIRST_PHOTO_RIGHTS_HANDOFF_20261028.md) · [Full 200-photo decision ledger](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/fabaceae-photo-200-decisions.json)

## Private real-photo learner (desktop and mobile passed)

[Open test instructions and download the ZIP with actual photos](TEST_THE_FABACEAE_LEARNER.md) · [Successful browser QA](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40786758255)

The cumulative staged archive now has **82 source-verified originals covering 54 of 91 species**. The most recent downloadable test site is linked from the review guide. This is not a declaration of anatomy-arrow completeness; public Pages remains disabled.

[Pass-3 Commons/GBIF migration handoff — 70 publicly licensed sources](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/FABACEAE_PHOTO_PASS3_HANDOFF_20261028.md)

[Pass-4 handoff — 82 archived originals, 75 independently licensed and 7 owner-authorized](https://github.com/Crking92/Hays-Botany-Fabaceae/blob/staging/fabaceae-metadata/migration/FABACEAE_PASS4_COMMONS_AND_OWNER_HANDOFF_20261028.md)

**Rights distinction:** the private gallery may show all 82 originals, but seven retain all-rights-reserved licenses on iNaturalist and are shown under direct source-owner authorization only. They are not unrestricted CC photographs.

## Next controlled passes

1. Cross-reference the 200 original image blobs against per-species `image-sources.csv` and current upstream rights; do not treat a CSV license claim as permission to publish.
2. Transfer only individual photos whose identity, source, creator and allowed reuse are actually verified. Retain undecided images as tracked holds.
3. Build a real, field-first learner with diagnostic images and valid source credits; keep layout consistent with the Asteraceae and original Hays Botany sites.
4. Test desktop/mobile, gallery loading and license restrictions before any separate public Pages approval or hub navigation cutover.

**Guardrails:** no restricted history publicization, no unverified photos, no fabricated arrows and no changes to existing public learner during staging.
