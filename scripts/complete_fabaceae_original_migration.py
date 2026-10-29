#!/usr/bin/env python3
"""Complete EXACT original-file Fabaceae migration, without approving any photo for display.

291 canonical text files at original paths, 82 already approved private gallery originals,
118 held originals in segregated PRIVATE quarantine. All 491 Git SHA-1 blobs verified.
A migrated/archived image is NOT a licensed or published image.
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from collections import Counter
ROOT=Path(sys.argv[1]).resolve()
SOURCE=Path(sys.argv[2]).resolve()
MIG=ROOT/"migration"
ledger=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
decisions=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
public_compatible=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
owner_only=json.loads((MIG/"fabaceae-private-owner-photo-ledger.json").read_text())
census=ledger["census"]
assert census["source_total_files"]==491
assert census["metadata_files"]==291
assert census["original_photo_files"]==200
assert census["source_original_image_bytes"]==42538089
assert len(ledger["files"])==491
assert len(decisions)==200
assert len(public_compatible)==75
assert len(owner_only)==7
assert set(public_compatible).isdisjoint(owner_only)
family_tree=subprocess.check_output(
    ["git","-C",str(SOURCE),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()
assert family_tree==census["source_family_subtree_sha"], "CANONICAL_FAMILY_TREE_CHANGED"
assert (ROOT/"config/collection.json").is_file()
config=json.loads((ROOT/"config/collection.json").read_text())
assert config["publication"]["enabled"] is False
assert config["family_assignments"]==["Fabaceae"] or "Fabaceae" in config["family_assignments"]
assert json.loads((ROOT/"data/collection-index.json").read_text())["authority"]=="STAGING_ONLY"
def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()
files={r["path"]:r for r in ledger["files"]}
assert len(files)==491
image_paths={p for p,r in files.items() if r["category"]=="SOURCE_IMAGE_ORIGINAL"}
text_paths={p for p,r in files.items() if r["category"]=="SCIENTIFIC_TEXT_OR_PROVENANCE"}
assert len(image_paths)==200 and len(text_paths)==291
by_decision={r["source_path"]:r for r in decisions}
assert len(by_decision)==200 and set(by_decision)==image_paths
assert {p for p,r in by_decision.items() if r["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}==set(public_compatible)
assert {p for p,r in by_decision.items() if r["status"]=="STAGED_PRIVATE_OWNER_PERMISSION"}==set(owner_only)
held={p for p,r in by_decision.items() if r["status"]=="HOLD"}
assert len(held)==118
assert held.isdisjoint(public_compatible) and held.isdisjoint(owner_only)
reserved_root=MIG/"private-original-photo-holds"
reserved_root.mkdir(parents=True,exist_ok=True)
stats=Counter()
records=[]
for path in sorted(files):
    record=files[path]
    source_file=SOURCE/path
    assert source_file.is_file(),f"Original source vanished: {path}"
    original=source_file.read_bytes()
    assert len(original)==record["size_bytes"],f"Wrong original size: {path}"
    assert git_blob(original)==record["git_blob_sha"],f"Wrong original Git blob: {path}"
    if path in text_paths:
        dest=ROOT/path
        assert dest.is_file(),f"Previously staged text missing: {path}"
        assert dest.read_bytes()==original,f"Text content changed: {path}"
        category="SOURCE_SCIENTIFIC_AND_CREDIT_TEXT"
        location=path
        stats["source_text_byte_exact"]+=1
    else:
        decision=by_decision[path]
        if decision["status"]=="HOLD":
            # Retain unapproved originals in a segregated private location. They
            # must NEVER enter the photo learner / dist / public Pages resources.
            subpath=Path(path).relative_to("content/taxa/Fabaceae")
            dest=reserved_root/subpath
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                assert dest.read_bytes()==original, f"Existing held file hash mismatch: {dest}"
            else:
                dest.write_bytes(original)
            category="PRIVATE_QUARANTINE_NEVER_PUBLISH_WITHOUT_RIGHTS_APPROVAL"
            location=dest.relative_to(ROOT).as_posix()
            stats["source_held_images_byte_exact_private"]+=1
        else:
            dest=ROOT/path
            assert dest.is_file(),f"Approved staged original missing: {path}"
            assert dest.read_bytes()==original,f"Staged image differs from source: {path}"
            if decision["status"]=="STAGED_PRIVATE_OWNER_PERMISSION":
                category="PRIVATE_OWNER_PERMISSION_NOT_PUBLIC_CC"
                stats["source_owner_photos_byte_exact"]+=1
            else:
                category="CURRENT_LICENSE_SOURCE_CHECKED_GALLERY_ORIGINAL"
                stats["source_cc_photos_byte_exact"]+=1
            location=path
        assert git_blob(dest.read_bytes())==record["git_blob_sha"]
        stats["image_bytes_migrated"]+=len(original)
    records.append({
        "original_source_path":path,
        "private_staging_path":location,
        "git_blob_sha":record["git_blob_sha"],
        "size_bytes":record["size_bytes"],
        "preservation_class":category,
        "display_authorized":(path in public_compatible or path in owner_only),
        "source_license_status":(by_decision[path]["status"] if path in image_paths else "SOURCE_TEXT"),
        "public_deploy_authorized":False,
    })
assert len(records)==491
assert stats["source_text_byte_exact"]==291
assert stats["source_cc_photos_byte_exact"]==75
assert stats["source_owner_photos_byte_exact"]==7
assert stats["source_held_images_byte_exact_private"]==118
assert stats["image_bytes_migrated"]==42538089
all_migrated={x["private_staging_path"] for x in records}
assert len(all_migrated)==491
actual_hold_files={p.relative_to(ROOT).as_posix() for p in reserved_root.rglob("*") if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".png",".webp")}
expected_holds={x["private_staging_path"] for x in records if x["source_license_status"]=="HOLD"}
assert actual_hold_files==expected_holds, "Untracked or missing private-original hold files"
actual_gallery_orig={p.relative_to(ROOT).as_posix() for p in (ROOT/"content/taxa/Fabaceae").rglob("*")
    if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".webp",".png")}
assert actual_gallery_orig==set(public_compatible)|set(owner_only)
# Validate every original source-relative reference to existing local image source
# or a current non-local URL. This is preservation, not a claim of URL liveness.
all_species=list((ROOT/"content/taxa/Fabaceae").glob("*/*/species.json"))
assert len(all_species)==91
referenced_local=[]
remote_links=[]
for species in all_species:
    card=json.loads(species.read_text())
    for row in card.get("images",[]) or []:
        if not isinstance(row,dict):continue
        rel=row.get("file") or ""
        if rel.startswith(("http://","https://")):
            remote_links.append({"species":card.get("id"),"url":rel})
            continue
        if rel.startswith("images/"):
            src=species.parent/rel
            relative=src.relative_to(ROOT).as_posix()
            assert relative in image_paths,f"Missing original image source reference: {relative}"
            referenced_local.append(relative)
# Local refs may also exist in other metadata (in source 291 text files).
summary={
    "status":"FABACEAE_ALL_ORIGINAL_491_FILES_COPIED_PRIVATE_HANDOFF_PASS",
    "original_family_tree_sha":family_tree,
    "original_source_files":491,
    "byte_exact_files_confirmed_in_family_repo":491,
    "original_text_credit_taxonomy_files_verified":291,
    "original_image_files_migrated_total":200,
    "original_image_bytes_migrated":stats["image_bytes_migrated"],
    "verified_cc_gallery_original_files":75,
    "owner_permission_private_gallery_files":7,
    "held_source_originals_physically_quarantined_private":118,
    "original_image_files_left_in_canonical_hub":200,
    "source_images_missing_from_family_repo":0,
    "original_species_count":91,
    "original_species_with_gallery_originals":len({v["species_id"] for v in list(public_compatible.values())+list(owner_only.values())}),
    "local_source_image_references_checked":len(referenced_local),
    "unique_source_image_refs":len(set(referenced_local)),
    "external_linked_images_in_species_cards":len(remote_links),
    "external_urls_physically_transferred":False,
    "gallery_restrictions_preserved":True,
    "hub_content_modified":False,
    "public_family_site_deployed":False,
    "public_repo_visibility_change":False,
    "family_site_ready_to_merge_live":False
}
(MIG/"fabaceae-all-original-491-file-transfer-manifest.json").write_text(
    json.dumps({"summary":summary,"files":records},indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-original-migration-completion-summary.json").write_text(
    json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-external-image-url-inventory.json").write_text(
    json.dumps({"count":len(remote_links),"images":remote_links},indent=2,ensure_ascii=False)+"\n")
(reserved_root/"DO_NOT_PUBLISH_README.txt").write_text(
    "PRIVATE ORIGINAL PHOTO HOLDS — DO NOT PUBLISH, MOVE INTO SITE DIST, OR SERVE.\n"
    "The original photos are preserved byte-identically only to finish the existing\n"
    "Fabaceae family source migration, not to grant reuse rights.\n"
    "See migration/fabaceae-photo-200-decisions.json for source-specific reasons.\n"
    "The central Hays-County-Botany source remains untouched and authoritative.\n"
)
print("FABACEAE_ALL_491_ORIGINAL_FILES_TRANSFER_PASS",json.dumps(summary,sort_keys=True),flush=True)
