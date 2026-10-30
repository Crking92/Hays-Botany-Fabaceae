# Fabaceae — all 75 vetted archive photographs restored; 88-image live QA

**Date:** October 30, 2026

## Verified public gallery

- **91/91** species lessons accessible.
- **59/91** species currently display at least one public-eligible photograph.
- **88** published photographs; **32 species** currently have no published photograph.
- [Latest live original-image verification](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/41063761970): **PASS**, all **91** species cards checked and **88/88** deployed image URLs fetched and compared byte-for-byte to the repository originals, no new photographs collected.
- The first deployment-time QA got a temporary HTTP 503, so the workflow now retries transient 429/5xx/connection failures. The subsequent live verification passed.
- Verified Git tree coverage of the 75 individual image records in the staged, source-checked `migration/fabaceae-verified-photo-ledger.json`: **75/75 exact filenames are present under the correct species folder in `main/site/media/`**. Original source Git blob hashes are pinned for all newly promoted GBIF, iNaturalist, and Dalea frutescens records. Historical strict Commons source audits remained in place.

## Changes made in this continuation

1. Published seven original, individually audited iNaturalist CC BY or CC BY-SA photos: *Desmodium paniculatum*, *Galactia canescens*, *Hylodesmum nudiflorum*, *Kummerowia striata*, *Lespedeza texana*, *Pediomelum linearifolium*, and *Pediomelum tenuiflorum*.
2. Published the remaining 20 independently audited archived GBIF CC BY 4.0 photos, including prairie clovers, *Erythrina herbacea*, *Gleditsia triacanthos*, *Melilotus albus*, *Mimosa roemeriana*, *Rhynchosia senna*, and *Sesbania drummondii*. These were restored in two bounded runs of 11 and 9.
3. Corrected *Dalea frutescens* 01-habit historical Commons metadata using the previously recorded exact photographer (**Miwasatoshi**), versioned **CC BY-SA 4.0**, source page and original Git image hash, releasing the last held record from the 75-photo vetted archive.
4. Restorer checks individual preapproved original-source photos against source, creator, license, taxon and Git blob SHA. Unknown, private-use, noncommercial-conditional or unavailable media were **not** generically released.
5. Fixed verification workflow resilience to transient GitHub Pages HTTP 503 responses.

No original source image was deleted or overwritten. No new external image was harvested for the public gallery. The original Hays-County-Botany botanical library remains untouched. Paused automations remain paused. Anatomy arrows and field-ID accuracy were not certified by these image-rights checks.

## Remaining image reference holds

The public source filtering reports **130 of 218 photo metadata records held**:
- **110** with license/permission insufficient under the current strict photo-specific public release gate, including CC BY-NC and private owner-authorized reference images requiring different treatment from unrestricted CC.
- **18** external URL-only references: all accounted for, no local original bytes in the 491-file migration.
- **2** with unresolved exact individual photo identity/license: *Desmanthus leptolobus* and *Mimosa latidens*.

Of the **200 original image files** transferred, **75** have the previously verified public-eligible archive status and now display; **7** were explicitly **private-project-only photographer-authorized**, not public CC grants; the other **118** have unresolved public release or source-image proof. The 88 published gallery photos and 200 source file inventory have different scopes; do not subtract one from the other.

### Next rights-specific review candidates (do not auto-release)

An Oct 30 Commons source-page review independently confirmed the posted rights labels for five previously held **exact page titles**, but **did not verify the archived bytes/pixels against those original current source images**:

| Historical source file / taxon | Source-page rights confirmed | Remaining gate |
|---|---|---|
| *Desmanthus illinoensis* `illinoensis-seeds.jpg` | [Commons source](https://commons.wikimedia.org/wiki/File:Desmanthus_illinoensis_seeds.jpg): Steve Hurst, USDA federal public domain | Compare historical archived JPEG to this exact Commons source image |
| *Desmanthus velutinus* `velutinus-usda-recon.jpg` | [Commons source](https://commons.wikimedia.org/wiki/File:Desmanthus_velutinus.jpg): USDA NRCS, federal public domain | Verify archive pixels/derivative |
| *Senegalia roemeriana* `02-flat-pods.jpg` | [Commons source](https://commons.wikimedia.org/wiki/File:Acacia_roemeriana_01nsh.jpg): Tracey Slotta, USDA public domain | Verify archive pixels |
| *Styphnolobium affine* `commons-styphnolobium-affine.jpg` | [Commons source](https://commons.wikimedia.org/wiki/File:Styphnolobium_affine.jpg): Jen, CC0 1.0 | Verify archive pixels and duplicate handling |
| *Vachellia farnesiana* `02-thick-dark-pods.jpg` | [Commons source](https://commons.wikimedia.org/wiki/File:Starr-030202-0023-Vachellia_farnesiana-seed_pods-Wailea_670-Maui_(23991674164).jpg): Forest & Kim Starr, CC BY 3.0 US | Verify archive pixels and accurate attribution |
| *Desmanthus acuminatus* `desmanthus-acuminatus-pods.jpg` | [Claimed Commons page](https://commons.wikimedia.org/wiki/File:Desmanthus_acuminatus_pods.jpg) was inaccessible in this check | Current photo page and pixel proof required |

These six are **not** included in the 88-photo count until original-image matching independently succeeds. Keep them on hold, and do not substitute other species photos.

## Next recommended pass

Investigate archived Commons and original source images from the five license-supported source pages above by exact image/pixel comparison, followed by another per-photo public release audit. The separate seven Glass Root Garden originals remain under recorded **private-only** authorization, so do not publish them or relabel them CC BY without an explicit public-use grant. Re-check rights individually before accepting any CC BY-NC image for the noncommercial site.

Full earlier audit: [October 30 18-reference and archive recovery](FABACEAE_REMOTE_REFERENCE_AND_ARCHIVED_CC_BY_PASS_20261030.md).
