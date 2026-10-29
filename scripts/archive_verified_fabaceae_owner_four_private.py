#!/usr/bin/env python3
"""Archive four exact-source photographer-granted originals to PRIVATE learner only.

No public CC license is inferred from owner authorization or old source CSV claims.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
from collections import Counter
SRC=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
MIG=ROOT/"migration"
source=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
audit=json.loads((MIG/"fabaceae-owner-four-audit.json").read_text())
decisions=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
cc=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
owner_path=MIG/"fabaceae-private-owner-photo-ledger.json"
owners=json.loads(owner_path.read_text()) if owner_path.is_file() else {}
assert len(audit["entries"])==4 and audit["summary"]["exact_owner_photos_verified"]==4
assert len(decisions)==200 and len(cc)>=70
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==source["census"]["source_family_subtree_sha"]
originals={x["path"]:x for x in source["files"] if x["category"]=="SOURCE_IMAGE_ORIGINAL"}
def sha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
by_path={d["source_path"]:d for d in decisions}
for x in audit["entries"]:
 path=x["source_path"]
 assert x["status"]=="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY"
 assert x["sitewide_public_cc_license_not_inferred"] is True
 assert x["photo_observation_link_verified"] and x["pixel_phash_distance"]<=12
 assert x["current_attribution"] and "Calvin King" in x["current_attribution"]
 assert x["current_license"] is None
 assert x["source_license_claim"] in ("Owner-authorized private study","CC BY 4.0 (direct photographer grant)")
 assert path in originals and by_path[path]["species_id"]==x["species_id"]
 assert by_path[path]["status"] in ("HOLD","STAGED_PRIVATE_OWNER_PERMISSION")
 assert by_path[path]["claimed_creator"]=="Glass Root Garden"
 b=(SRC/path).read_bytes()
 assert len(b)==originals[path]["size_bytes"]
 assert sha(b)==originals[path]["git_blob_sha"]==by_path[path]["source_git_blob_sha"]
 dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(b)
 assert sha(dest.read_bytes())==originals[path]["git_blob_sha"]
 evidence={
  "creator":"Glass Root Garden (Calvin King)",
  "license":"Owner-authorized private project use; original photo all rights reserved",
  "license_url":"",
  "source_page":x["photo_page"],
  "observation_id":x["observation_id"],"photo_id":x["photo_id"],
  "observed_taxon":x["current_taxon"],
  "current_inat_license_code":x["current_license"],
  "current_inat_attribution":x["current_attribution"],
  "photo_image_pixel_distance":x["pixel_phash_distance"],
  "pixel_phash_distance":x["pixel_phash_distance"],
  "provenance":"INAT_EXACT_OBSERVATION_AND_OWNER_DIRECT_PERMISSION",
  "permission_basis":x["owner_permission_basis"] or "Photographer direct CC BY 4.0 grant claimed in original source CSV; do not assume current iNaturalist license changed",
  "public_cc_license_not_inferred":True
 }
 by_path[path].update(status="STAGED_PRIVATE_OWNER_PERMISSION",evidence=evidence,
  destination_path=path,pixel_verified=True,publication_approved=False,
  private_rights_review_only=True,diagnostic_annotations_verified=False)
 by_path[path].pop("reason",None)
 owners[path]=by_path[path]
assert len(owners)==4
assert set(cc).isdisjoint(owners)
assert len(cc)+len(owners)+sum(x["status"]=="HOLD" for x in decisions)==200
assert set(cc)=={x["source_path"] for x in decisions if x["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}
assert set(owners)=={x["source_path"] for x in decisions if x["status"]=="STAGED_PRIVATE_OWNER_PERMISSION"}
actual={p.relative_to(ROOT).as_posix() for p in (ROOT/"content/taxa/Fabaceae").rglob("*")
 if p.is_file() and p.suffix.lower() in {".jpg",".jpeg",".webp",".png"}}
assert actual==set(cc)|set(owners)
summary={
 "status":"FABACEAE_AUTHOR_EXACT_SOURCE_PRIVATE_PREVIEW_ONLY",
 "original_photos_total":200,"public_compatible_archived":len(cc),
 "owner_permitted_private_photos_archived":len(owners),
 "cumulative_originals_archived":len(cc)+len(owners),
 "source_original_photos_held":200-len(cc)-len(owners),
 "species_with_any_archived_photo":len({x["species_id"] for x in list(cc.values())+list(owners.values())}),
 "private_owner_species":len({x["species_id"] for x in owners.values()}),
 "new_private_owner_images":4,"public_compatible_owner_grants_not_inferred":True,
 "public_pages_deployed":False,"original_hub_changed":False
}
(MIG/"fabaceae-private-owner-photo-ledger.json").write_text(json.dumps(owners,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-photo-200-decisions.json").write_text(json.dumps(decisions,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-owner-four-private-archive-summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_OWNER_FOUR_PRIVATE_ARCHIVE",json.dumps(summary,sort_keys=True),flush=True)
