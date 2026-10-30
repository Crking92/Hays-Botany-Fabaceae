# Fabaceae archived-photo continuation — October 30, 2026

## Summary: recovered archive-only photographs

Public Fabaceae Visual Learner now includes **43 of 91 species** with at least one photograph and **60 published photographs**. The [live 60-image byte verification](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/41060245702) passed after re-running once due to a temporary Pages HTTP 503 during deployment. All 91 species cards loaded; all 60 live image files matched the original bytes. **No external photos were downloaded as part of this pass.** Historical originals and staging branch remain preserved. The main Hays County Botany repository is read-only; inactive automations were not changed.

### Eleven more existing CC BY 4.0 originals published

A narrow allowlist was added to `scripts/restore_existing_source_public_media.py`. Every entry was already in the previously transferred source archive with a matching record in `migration/fabaceae-verified-photo-ledger.json`. Publication requires matching species path, creator, GBIF source page, exact media URL, recorded **CC BY 4.0** license, prior source pixel comparison, historical verified status and exact original Git blob SHA. The source cards retain their original terse `CC BY` claim; the public image caption gives the version from individually audited ledger evidence.

| Species | Recovered archived image(s) | Creator |
|---|---:|---|
| *Amorpha canescens* | 1 | Cleveland Powell |
| *Amorpha roemeriana* | 2 | Cleveland Powell; Reid Hardin |
| *Astragalus crassicarpus* var. *berlandieri* | 2 | Michelle W. （鍾偉瑋） |
| *Astragalus lindheimeri* | 1 | CH Hemphill |
| *Cercis canadensis* subsp. *mexicana* | 1 | Michelle W. （鍾偉瑋） |
| *Dalea multiflora* | 1 | Cleveland Powell |
| *Desmodium psilophyllum* | 1 | Aspen Frisch |
| *Desmodium sessilifolium* | 2 | Michelle W. （鍾偉瑋） |

Source-verified photographic publication is not a claim of complete morphological/anatomical identification; the older expert-review notes are preserved.

## The 18 remote or missing records were not actually lost files

All **18** carry external `https://` URLs as their original `images[].file` value. None was a missing local JPEG/PNG within the original 491-file family migration. They are *references-only*, not installed media. They were left untouched, with original source URLs and credits preserved.

| Image-reference class | Records | Original record examples / action |
|---|---:|---|
| Wikimedia Commons public-domain or CC BY-SA links | 6 | *Amorpha canescens* (3), *Cercis canadensis* subsp. *texensis* (1), *Senna lindheimeriana* (2). Source pages recorded; external image bytes not included in prior archive. Only acquire after separately approved new retrieval and per-file review. |
| iNaturalist image links labeled CC BY | 4 | *Dalea enneandra* (1), *Dalea hallii* (2), *Dalea tenuis* (1). Exact photo-page links recorded; files are external-only. |
| iNaturalist links labeled CC BY-NC | 3 | *Dalea aurea*, *Dalea compacta*, *Dalea purpurea*. Noncommercial status and exact source must remain individually reviewed; no archival original. |
| University/source images with public reuse unverified | 5 | *Amorpha roemeriana* (1), *Senna lindheimeriana* (4). Keep source links only; no public gallery copy without explicit clearance. |
| **Total** | **18** | **No orphaned downloaded originals identified**. |

Note: these categories describe the historical metadata claims, not a fresh verification that a photographer's current license has not changed. The 18 links should remain accounted for instead of appearing as missing transfer failures.

## Current remaining photo metadata holds

Of 218 original image metadata records, **60 are installed** and **158 held** in the source-filtered public gallery:
- **138** have restricted, shorthand or otherwise not-yet-cleared license information under the **current automated public filter**. This category includes some items in the historical 75-photo independently verified archive that are good candidates for exact-image rights recovery; it does not mean all 138 are permanently restricted.
- **18** are external URL references without a local original image file.
- **2** still lack enough evidence for image-specific publication: *Desmanthus leptolobus* (iNaturalist photo 734524728) and *Mimosa latidens* (observation 173281412).

This leaves **48 species with no published photo**. Next pass should continue narrow, source-verified CC BY/CC BY-SA and original-owner images from the physically archived, already audited originals, not harvest new external images. New images, anatomy or taxon decisions must go to the assigned family repository, not the original read-only hub.

## Relevant checkpoints

- [Earlier five exact-photo recovery and remaining two holds](FABACEAE_SEVEN_RECORD_RIGHTS_PASS_20261029.md)
- [Fabaceae source transfer and baseline photo QA](FABACEAE_SOURCE_AND_GALLERY_QA_CHECKPOINT_20261029.md)
- [Public live source/photo test](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/runs/41060245702)
