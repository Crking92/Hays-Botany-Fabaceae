# Fabaceae — seven-record archived photo recovery (2026-10-29)

## Outcome

Five exact archived original photos restored from seven outstanding source-rights records. Source-gallery records now report **49 released photos across 35 of 91 species**, up from 44 photos across 31 species. Every species lesson remains in place. **56 species** still have no released photograph. No external photographs were downloaded for gallery replacement; no historical original bytes were deleted or rewritten. This is public-photo source coverage, **not a claim that all diagnostic anatomy is botanically verified**.

## Five recovered exact archived photographs

| Species | Original image file | Source | Creator / photo rights | Existing-source audit |
|---|---|---|---|---|
| *Astragalus leptocarpus* | `gbif-manual-5108100988-d4eff7545.jpg` | [GBIF occurrence 5108100988](https://www.gbif.org/occurrence/5108100988), media/photo 479347175 | Nautilus 211; CC0 1.0 | Archived Git blob `ff0dc7b5109f49cd8abdc0c3ffd105251e661555` |
| *Astragalus plattensis* | `gbif-manual-5140729847-19b7a5e80.jpg` | [GBIF occurrence 5140729847](https://www.gbif.org/occurrence/5140729847), media/photo 494561662 | Donna H.; CC0 1.0 | Archived Git blob `c198188a68107d4449ff083422f5d18724564761` |
| *Dalea hallii* | `library-review014-725ce09df227f6c.jpg` | [GBIF occurrence 6186158439](https://www.gbif.org/occurrence/6186158439), media/photo 628316900 | Vince Hale; CC0 1.0 | Archived Git blob `248af4a9ced2d582785f767ace9d8e63faa8724e` |
| *Senna pilosior* | `gbif-first-6431822939-9ca58a139a.jpg` | [GBIF occurrence 6431822939](https://www.gbif.org/occurrence/6431822939), media/photo 692204066 | April Coulon; CC0 1.0 | Archived Git blob `022ecb3f31a5d0fcc2f6af35c0e4c8bace42a61e` |
| *Senegalia wrightii* | `01-flower-spike.jpg` | [iNaturalist Wright Acacia guide](https://www.inaturalist.org/guide_taxa/1557820), source photo 23060929 | Alison Northup; CC BY 4.0 | Original `SOURCES.txt` and `image-sources.csv` explicitly identify that exact guide image; archived Git blob `7123904bd721d2f259c44021c829a2b6c63619e4` |

The original family staging `migration/fabaceae-verified-photo-ledger.json` and `migration/fabaceae-gbif43-source-research.json` contained exact-source, image-pixel and creator/license evidence for the four GBIF images. Publication code now recognizes **only** these fixed CC0 image records and enforces their original Git blob SHA before copying media. The Wright acacia image is likewise pinned to the exact iNaturalist guide photo, taxon, photographer, CC BY license, media URL and archived bytes. No generic GBIF or iNaturalist photo clearing was added.

**Teaching caveat:** Source taxon determinations were preserved; this pass did not certify flowers, leaflets, pods, anatomical arrows, close-up diagnostic features or field readiness.

## Two original records still held

1. *Desmanthus leptolobus* `desmanthus-leptolobus-texas-face-cc0.jpg` — [iNaturalist photo 734524728](https://www.inaturalist.org/photos/734524728). Archived record states CC0 but identifies the creator only as `no rights reserved`, without a photographer or independently verified exact-photo license response. Keep held until creator/photo license can be resolved.
2. *Mimosa latidens* `mimosa-latidens-provisional-face.jpg` — [iNaturalist observation 173281412](https://www.inaturalist.org/observations/173281412). Original metadata credits Michelle Wong and CC BY 4.0, with an FSUS direct image link. The observation URL is not itself an exact photo page and current independent photo-license/identity verification was unavailable. Keep held until the exact photo is matched and credited.

The latest remaining 169 held image metadata records are: **149** restricted or unverified license, **18** missing or remote local original file, and **2** insufficient individual-photo source evidence. These are reference records, not counts of unique photographs.

## Boundaries and release testing

All 91 original species lessons retained. The original `Crking92/Hays-County-Botany` hub remains read-only, new content stays in the assigned Fabaceae family repository, and paused automations are unchanged. The family `main/site` is the public licensed gallery, not an unfiltered publishing of archive holds. Use [the live site image QA workflow](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/workflows/verify-public-fabaceae-gallery.yml) to confirm all live hosted bytes after each expansion.
