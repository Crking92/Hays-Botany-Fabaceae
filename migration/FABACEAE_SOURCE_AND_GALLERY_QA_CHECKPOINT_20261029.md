> **LATEST OCTOBER 29 RECOVERY — VERIFIED LIVE:** **35/91 Fabaceae species** now have **49 published photographs**, up from 31/44 at the previous checkpoint and 13/20 before both recovery passes. [Live original-byte QA run 40939335928](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40939335928) passed all **91 species cards** and **49/49 original media URLs**. Five specific pre-existing originals were restored from seven reviewed records: two *Astragalus* species, *Dalea hallii*, *Senna pilosior* and *Senegalia wrightii* (one additional view for an already pictured *Astragalus*; four species gained a first photo). The [seven-record rights ledger](FABACEAE_SEVEN_RECORD_RIGHTS_PASS_20261029.md) records exact source URLs, author/license statements, Git image hashes and the two remaining holds (*Desmanthus leptolobus*, *Mimosa latidens*). **56 species lack public photographs** and **169/218 metadata image records are held**: 149 restricted or unverified licenses, 18 remote/nonlocal originals, and 2 insufficiently proved individual photo sources. No new photographs were collected, no original source files removed, no hub botanical changes, and no paused automation resumed. Older audit figures below are historical snapshots.

# Fabaceae — existing-source migration and public-gallery QA checkpoint

Date: October 29, 2026. Source-only audit for the next Hays Botany family after Asteraceae.

## What was physically transferred

The prior pinned original-file migration reports **491/491** Fabaceae source files in the family repo staging branch, including **91 botanical species records**, **291 text/credit files**, and **200 original source image files**. An earlier hash audit verified those originals against the pinned original. 82 images were within the staged learner's original content folders, and 118 original photographs were kept in a separate rights-hold archive. **This turn did not repeat that 491-file hash audit**, and it did not remove, alter or overwrite those originals.

This repository and its historical staging branch are now PUBLIC. The folder name `migration/private-original-photo-holds` is a historical label, not actual privacy protection. Keep unclear photo rights separately reviewed.

## Live public site

- **91/91** botanical species cards exist in the dedicated family site.
- **11/91** species have a public rights-cleared photograph.
- **18** publicly displayed original source photographs are recorded; **80 species still have no published photograph**.
- [Full live GitHub Pages verification passed](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/40934030037), fetching all 91 species cards and comparing the bytes of **18/18** hosted image URLs with the source files in the current public `main/site/media` tree.
- No additional photos were acquired by this QA pass.

## Exact original media-rights inventory

The family script `scripts/restore_existing_source_public_media.py` accounts for **218** source image **metadata records** (not necessarily distinct files), publishing **18** images and holding **200** metadata records from the public image gallery.

- `unverified_license_or_restricted`: **149** source records
- `missing_or_remote_original_file`: **18** source records
- `photo_specific_public_source_unverified`: **9** source records
- `creator_unverified`: **2** source records
- `public_reuse_flag_unverified`: **20** source records
- `public_reuse_not_cleared`: **2** source records

The detailed per-species hold list is in [site/photo-source-migration-report.json](../site/photo-source-migration-report.json). These source assets are accounted for and are **not to be replaced indiscriminately** with newly gathered photos. Public noncommercial CC BY-NC may be usable where each individual photo carries that license, but NC terms are not silently treated as unrestricted CC BY. All-rights-reserved and uncertain licensing remain held.

## Routing and next work

The source-edit branch is **`staging/fabaceae-metadata`**, per [AGENTS.md](../AGENTS.md); the public family site is derived on `main/site`. The original hub stays read-only fallback for historical botanical content. No paused photo collection or old installers restarted.

Next step: classify the 80 photo-empty species against the staged 200 original images and the 218 metadata photo references; identify individually documented Commons/CC0/CC BY/author-controlled source photos that are **already** present, then restore exact existing bytes to the proper species cards, followed by a new complete live website photo smoke test.
