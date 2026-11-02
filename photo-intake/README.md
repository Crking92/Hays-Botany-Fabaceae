> **Current photo-first instructions (November 2, 2026):** See [the shared family policy](../workflow/PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02.md). Publish useful credited general views of already indexed species as soon as exact-image rights and a basic species sanity check are substantiated. No anatomy arrows or finished lessons are required. Every source image needs its matching metadata sidecar; copies in a ZIP or staging branch do not count until the family Pages gallery serves them. Keep restricted or unresolved photo bytes out of **every** branch of a public repository.

**Two accepted approval paths:** (1) an actual named photo reviewer with real documented evidence; or (2) the owner's documented standing photo-first policy with `approval_mode: OWNER_STANDING_PHOTO_FIRST_POLICY`, `policy_ref: PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02`, and truthful `review_operator`, `source_review_evidence`, `taxon_review_evidence` and `approval_note` values. Both still require `rights_approved_for_public: true`, `taxon_reviewed: true`, verified creator, exact-photo HTTPS source, license/version/URL, image bytes and credible source proof. **Never fabricate reviewer evidence, IDs or approvals.**

**Licenses:** verifiable CC0, CC BY and CC BY-SA photos are normally allowed. CC BY-NC 4.0 / CC BY-NC-SA 4.0 are conditionally permitted **only** with an actually noncommercial educational family site, an individually checked license, and `noncommercial_site_use_confirmed: true` for that photo. Preserve explicit NC reuse limits, attribution and adaptation/ShareAlike requirements. Hold ND, ARR and uncertain rights. If the publisher refuses otherwise eligible media, fix its implementation or record the hold; don't bypass guards. New species still need a reviewed index/card installation before automatic general-gallery intake.

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
