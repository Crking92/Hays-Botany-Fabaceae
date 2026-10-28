#!/usr/bin/env python3
"""Transfer only exact GBIF multimedia source-confirmed Fabaceae originals into private staging."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from collections import Counter
SRC=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
MIG=ROOT/"migration"
evidence=json.loads((MIG/"fabaceae-gbif43-source-research.json").read_text())
current=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
ledger=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
summary2=json.loads((MIG/"fabaceae-photo-pass2-summary.json").read_text())
inventory=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
assert evidence["summary"]["source_original_gbif_photo_holds"]==43
assert evidence["summary"]["multimedia_and_pixel_verified_candidates"]==35
assert len(evidence["entries"])==43 and len(current)==200
assert len(ledger)==summary2["originals_physically_byte_verified"]==35
assert summary2["source_originals_held"]==165
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==summary2["canonical_source_subtree_sha"]
originals={x["path"]:x for x in inventory["files"] if x["category"]=="SOURCE_IMAGE_ORIGINAL"}
records={x["source_path"]:dict(x) for x in current}
assert len(records)==len(originals)==200
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
new={}
for e in evidence["entries"]:
    if e["status"]!="CANDIDATE_SOURCE_AND_PIXEL_VERIFIED":continue
    rel=e["source_path"]
    assert rel in records and rel in originals and rel not in ledger
    row=records[rel]
    assert row["status"]=="HOLD" and row["species_id"]==e["species_id"]
    assert row["claimed_source_page"]==e["gbif_occurrence_url"]
    ev=e["evidence"]
    assert ev["source_page"]==row["claimed_source_page"]
    assert ev["pixel_phash_distance"]<=12
    assert ev["creator"] and ev["media_identifier"].startswith("https://")
    assert ev["provenance"]=="GBIF_CURRENT_MULTIMEDIA_EXACT_SOURCE"
    assert ev["license"].startswith(("CC BY ","CC BY-SA ","CC0 "))
    assert re.fullmatch(r"https://creativecommons.org/(licenses/(by|by-sa)/[234](?:\.\d)?|publicdomain/zero/1(?:\.0)?)/",ev["license_url"])
    original=(SRC/rel).read_bytes()
    assert len(original)==originals[rel]["size_bytes"]
    assert blob(original)==row["source_git_blob_sha"]==originals[rel]["git_blob_sha"]
    dest=ROOT/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(original)
    assert blob(dest.read_bytes())==row["source_git_blob_sha"]
    row.update(status="STAGED_PRIVATE_PUBLIC_COMPATIBLE",evidence=ev,
        destination_path=rel,pixel_verified=True,
        publication_approved=False,diagnostic_annotations_verified=False)
    row.pop("reason",None)
    row.pop("pass2_commons_recheck_reason",None)
    new[rel]=row
assert len(new)==35
merged={**ledger,**new}
assert len(merged)==70
updated=[records[x["source_path"]] for x in current]
assert len(updated)==200
assert set(merged)=={r["source_path"] for r in updated if r["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}
photos_on_disk={p.relative_to(ROOT).as_posix() for p in (ROOT/"content/taxa/Fabaceae").rglob("*")
                if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".png",".webp")}
assert photos_on_disk==set(merged),f"Unexpected or missing verified media: {photos_on_disk^set(merged)}"
summary={
    "status":"FABACEAE_GBIF_SOURCE_VERIFIED_PRIVATE_ARCHIVE_COMPLETE_NOT_PUBLIC",
    "source_original_photos_total":200,
    "original_photos_archived":len(merged),
    "source_original_photos_held":200-len(merged),
    "new_gbif_multimedia_photos_archived":len(new),
    "photo_covered_species":len({r["species_id"] for r in merged.values()}),
    "species_total":91,
    "held_reason_counts":dict(Counter(r.get("reason") for r in updated if r["status"]=="HOLD")),
    "held_gbif_multimedia_records":8,
    "source_family_subtree_sha":summary2["canonical_source_subtree_sha"],
    "main_hub_unchanged":True,
    "public_site_deployed":False,
    "diagnostic_arrow_approval":False
}
(MIG/"fabaceae-photo-200-decisions.json").write_text(json.dumps(updated,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-verified-photo-ledger.json").write_text(json.dumps(merged,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-photo-pass3-gbif-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print("FABACEAE_GBIF_ARCHIVE_PASS",json.dumps(summary,sort_keys=True),flush=True)
