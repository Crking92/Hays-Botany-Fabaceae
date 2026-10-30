# Approved public photo intake — Fabaceae

Each new image needs a matching `.jpg.json` or `.png.json` sidecar file in the SAME species folder.

**Important:** This folder and its entire Git history are PUBLIC. Upload only public-safe photographs for which the specified source/license/identity have been independently checked. A checked box is not legal permission. License and taxon review are human decisions. Uncertain rights or private-only specimens must stay outside the public repository.

Example path: `photo-intake/approved/amorpha-canescens/leadplant-flower.jpg` with matching `leadplant-flower.jpg.json`. Use this exact JSON structure, replacing every placeholder:

```json
{
  "species_id": "amorpha-canescens",
  "photo_file": "leadplant-flower.jpg",
  "status": "APPROVED_FOR_PUBLIC_FAMILY_SITE",
  "rights_approved_for_public": true,
  "taxon_reviewed": true,
  "approved_by": "Your name as image reviewer",
  "approval_note": "Describe how you verified this exact image license and identity (at least twelve characters)",
  "creator": "Exact photographer name",
  "source_page": "https://www.example.org/individual-photo-page",
  "source_page_is_exact": true,
  "license": "CC BY 4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "role": "Visible botanical features actually shown, without invented structures",
  "modifications": "Exact original / or list all modifications"
}
```

The example is **not** an approved real photograph or actual source URL. Do not copy its placeholder metadata into a real release. The `sha256` field is optional; if supplied it MUST equal the real file's hash.

Photo uploads lacking the paired approved metadata fail closed. The pipeline will not add new plants, fetch internet pictures, re-label rights-held archives, or silently alter the old hub.
