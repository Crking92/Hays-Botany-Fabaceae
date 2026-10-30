# Fabaceae — approved-photo auto-publication

This is a **public-repository, fail-closed intake**. Source and final website photography are publicly accessible in Git history; **do not upload private, ARR, uncertain, or unverified photographs to this intake**.

The newly connected [Fabaceae family lesson](https://crking92.github.io/Hays-Botany-Fabaceae/site/#family-lesson) is a separate family-level anatomy/photo introduction. Species lessons remain distinct.

## Adding one new approved photograph

1. Verify the actual species/diagnostic structures and individual photo copyright/license, original exact-photo source, creator and allowed changes. Select only CC0, CC BY or CC BY-SA with an exact permitted version. NC, ND, ambiguous license versions, private authorizations and ARR do **not** pass this strict public pipeline.
2. On branch `staging/fabaceae-metadata`, create/upload BOTH:
   - `photo-intake/approved/amorpha-canescens/leadplant-flower.jpg`
   - `photo-intake/approved/amorpha-canescens/leadplant-flower.jpg.json`
3. The matching JSON must contain `species_id`, `photo_file`, `status`, `rights_approved_for_public`, `taxon_reviewed`, `approved_by`, `approval_note`, `creator`, `source_page`, `source_page_is_exact`, `license`, `license_url`, `role`, `modifications`. See [fillable example](../../photo-intake/README.md).
4. Pushing the approved pair to that exact staging branch automatically runs [the release workflow](https://github.com/Crking92/Hays-Botany-Fabaceae/actions/workflows/auto-publish-approved-photos.yml).
5. The workflow decodes the actual image, verifies the registered species and approval fields, checks each photo path and original Git blob identity, regenerates that species's `verified_photos` gallery, both collection-level photo counts/thumbnail indexes, and commits to `main`. Normal GitHub Pages deployment then shows it on the family learner. No need to hand-edit the live website or hub.
6. If photo source, identity, metadata or existing website files disagree, release **stops** rather than overwriting older work. The human license claim is still the reviewer's responsibility; software cannot independently determine copyright permission from a checkbox.

Current limits: existing species **only**, supported JPG/PNG/WEBP images up to 25 MB; new species must be curated and published separately first. A single photo can have multiple anatomy lessons later, but this automation does not invent diagnostic arrows or crop photos.

This is a **Fabaceae pilot**. Reuse the same guarded pattern for other family sites only after a successful end-to-end photo test. The original Hays-County-Botany source and legacy learner remain unchanged.
