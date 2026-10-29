#!/usr/bin/env python3
"""Copy three separately owner-authorized photos after exact current observation proof.

The original images retain all rights reserved on iNaturalist. PRIVATE review only.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
SRC=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
EVIDENCE=Path(sys.argv[3]).resolve()
MIG=ROOT/"migration"
source=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
record=json.loads(EVIDENCE.read_text())
decisions=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
approved=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
owners=json.loads((MIG/"fabaceae-private-owner-photo-ledger.json").read_text())
assert len(record["entries"])==3 and record["summary"]["exact_observation_photo_matches"]==3
assert len(owners)==4 and len(approved)>=75
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==source["census"]["source_family_subtree_sha"]
originals={x["path"]:x for x in source["files"] if x["category"]=="SOURCE_IMAGE_ORIGINAL"}
by_path={x["source_path"]:x for x in decisions}
def sha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
for item in record["entries"]:
 path=item["source_path"]
 assert item["status"]=="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY"
 assert item["photo_observation_link_verified"] and item["pixel_phash_distance"]<=12
 assert item["current_attribution"] and "Calvin King" in item["current_attribution"]
 assert item["public_cc_not_inferred"] is True
 assert path in originals and path not in owners and path not in approved
 assert by_path[path]["status"]=="HOLD" and by_path[path]["claimed_creator"]=="Calvin King"
 assert int(item["photo_id"])==int(by_path[path]["claimed_source_page"].rsplit("/",1)[-1])
 b=(SRC/path).read_bytes()
 assert len(b)==originals[path]["size_bytes"]
 assert sha(b)==originals[path]["git_blob_sha"]==by_path[path]["source_git_blob_sha"]
 dest=ROOT/path
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(b)
 assert sha(dest.read_bytes())==originals[path]["git_blob_sha"]
 evidence={
  "creator":"Glass Root Garden (Calvin King)",
  "license":"Owner-authorized private project use; original photo all rights reserved",
  "license_url":"",
  "source_page":item["claimed_photo_url"],
  "observation_id":item["observation_id"],"photo_id":item["photo_id"],
  "observed_taxon":item["observed_taxon"],
  "current_inat_license_code":item["current_license"],
  "current_inat_attribution":item["current_attribution"],
  "pixel_phash_distance":item["pixel_phash_distance"],
  "provenance":"INAT_CONFIRMED_OWNER_USER_TAXON_OBSERVATION_AND_PHOTO_MATCH",
  "permission_basis":"Original photo-owner permission recorded as private study use in family source CSV; independent current iNaturalist photo remains all rights reserved",
  "public_cc_license_not_inferred":True
 }
 by_path[path].update(status="STAGED_PRIVATE_OWNER_PERMISSION",evidence=evidence,
  destination_path=path,pixel_verified=True,publication_approved=False,
  private_rights_review_only=True,diagnostic_annotations_verified=False)
 by_path[path].pop("reason",None)
 owners[path]=by_path[path]
assert len(owners)==7 and set(owners).isdisjoint(approved)
assert len(decisions)==200 and len({x["source_path"] for x in decisions})==200
assert len(approved)+len(owners)+sum(x["status"]=="HOLD" for x in decisions)==200
assert {x["source_path"] for x in decisions if x["status"]=="STAGED_PRIVATE_OWNER_PERMISSION"}==set(owners)
actual={p.relative_to(ROOT).as_posix() for p in (ROOT/"content/taxa/Fabaceae").rglob("*")
 if p.is_file() and p.suffix.lower() in {".jpg",".jpeg",".webp",".png"}}
assert actual==set(owners)|set(approved),f"Unaccounted original image: {actual^(set(owners)|set(approved))}"
summary={
"status":"FABACEAE_ALL_SEVEN_OWNER_SOURCES_VERIFIED_PRIVATE_ONLY",
"original_photo_files":200,
"strict_cc_originals_archived":len(approved),
"private_owner_originals_archived":len(owners),
"total_archived_originals":len(approved)+len(owners),
"originals_held":200-len(approved)-len(owners),
"species_with_any_archived_original":len({x["species_id"] for x in list(owners.values())+list(approved.values())}),
"source_originals_deleted":0,
"public_pages_enabled":False,
"owner_original_inaturalist_license_rewritten":False
}
(MIG/"fabaceae-photo-200-decisions.json").write_text(json.dumps(decisions,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-private-owner-photo-ledger.json").write_text(json.dumps(owners,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-owner-seven-private-archive-summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-owner-three-unlinked-evidence.json").write_text(EVIDENCE.read_text())
print("FABACEAE_OWNER_SEVEN_PRIVATE_ARCHIVED",json.dumps(summary,sort_keys=True),flush=True)
