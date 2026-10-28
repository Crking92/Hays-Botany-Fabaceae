#!/usr/bin/env python3
"""Copy exact Fabaceae scientific/credit text from unchanged canonical source.
No original photos, public rights, website publication or authority transfer.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

source=Path(sys.argv[1]).resolve()
target=Path(__file__).resolve().parents[1]
report_path=target/"migration/fabaceae-pinned-source-file-ledger.json"
inventory=json.loads(report_path.read_text(encoding="utf-8"))
census=inventory["census"]
assert census["source_repository"]=="Crking92/Hays-County-Botany"
assert census["destination_repository"]=="Crking92/Hays-Botany-Fabaceae"
assert census["original_photo_files"]==200 and census["metadata_files"]==291
assert census["species_json_records"]==91
# Newer unrelated hub commits are permitted only if the Fabaceae tree is byte-identical.
tree=subprocess.check_output(
    ["git","-C",str(source),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()
assert tree==census["source_family_subtree_sha"], (
    f"Fabaceae source changed since original audit: {tree}; stop and recensus"
)
assert len(inventory["files"])==491
assert len({f["path"] for f in inventory["files"]})==491
assert all(f["path"].startswith("content/taxa/Fabaceae/") for f in inventory["files"])
staged=[]
held=[]
for entry in inventory["files"]:
    rel=Path(entry["path"])
    if entry["category"]=="SOURCE_IMAGE_ORIGINAL":
        held.append(entry)
        continue
    assert entry["category"]=="SCIENTIFIC_TEXT_OR_PROVENANCE",rel
    assert rel.suffix.lower() in {".json",".csv",".txt"},rel
    original=source/rel
    assert original.is_file(),f"Missing source metadata: {rel}"
    blob=original.read_bytes()
    gitsha=hashlib.sha1(b"blob "+str(len(blob)).encode()+bytes([0])+blob).hexdigest()
    assert gitsha==entry["git_blob_sha"],f"Source metadata SHA mismatch: {rel}"
    destination=target/rel
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(blob)
    staged.append({"path":rel.as_posix(),"git_blob_sha":gitsha,"bytes":len(blob)})
assert len(staged)==291 and len(held)==200
species_files=sorted((target/"content/taxa/Fabaceae").glob("*/*/species.json"))
assert len(species_files)==91,len(species_files)
index=json.loads((target/"data/collection-index.json").read_text(encoding="utf-8"))
assert index["authority"]=="STAGING_ONLY" and index["collection_id"]=="fabaceae"
records=[]
for p in species_files:
    d=json.loads(p.read_text(encoding="utf-8"))
    assert d["family"]=="Fabaceae" and d["id"]==p.parent.name
    assert d["genus"]==p.parents[1].name
    records.append({
        "id":d["id"],"scientific_name":d["scientific_name"],
        "common_name":d.get("common_name",""),"family":"Fabaceae",
        "genus":d["genus"],"path":p.relative_to(target).as_posix(),
        "photo_publication_status":"SOURCE_METADATA_ONLY_NOT_CLEARED"
    })
assert len({r["id"] for r in records})==91
index.update({
    "entries":sorted(records,key=lambda r:r["id"]),
    "source_repository":census["source_repository"],
    "source_commit_sha":census["source_commit_sha"],
    "source_family_subtree_sha":tree,
    "public_website_ready":False,
    "note":"Exact source metadata only; 200 original photos are held for per-image rights audit."
})
(target/"data/collection-index.json").write_text(
    json.dumps(index,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
photos=[p for p in (target/"content/taxa/Fabaceae").rglob("*")
    if p.is_file() and p.suffix.lower() in {".jpg",".jpeg",".png",".tif",".tiff",".webp",".gif"}]
assert not photos, f"Image transfer must remain zero: {photos[:5]}"
summary={
    "status":"PRIVATE_FABACEAE_TEXT_ONLY_STAGING; NOT_PUBLIC",
    "canonical_source_tree_sha":tree,
    "original_source_commit_reference":census["source_commit_sha"],
    "species_records":len(records),
    "source_metadata_files_byte_verified":len(staged),
    "source_original_photos_accounted_for_but_not_moved":len(held),
    "photo_rights_approved":False,
    "photos_copied":0,
    "hub_authority_changed":False,
    "site_published":False,
}
(target/"migration/fabaceae-text-only-stage-summary.json").write_text(
    json.dumps(summary,indent=2)+chr(10),encoding="utf-8")
print("FABACEAE_TEXT_ONLY_STAGE_PASS",json.dumps(summary,sort_keys=True),flush=True)
