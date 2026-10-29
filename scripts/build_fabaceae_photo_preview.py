#!/usr/bin/env python3
"""Build a private, non-deployed real-photo Fabaceae learner from exact verified original files."""
import hashlib,json,shutil,sys
from collections import Counter
from pathlib import Path
from PIL import Image,ImageOps
SHELL=Path(__file__).resolve().parents[1]
STAGING=Path(sys.argv[1]).resolve()
DEST=SHELL/"dist"
config=json.loads((STAGING/"config/collection.json").read_text())
index=json.loads((STAGING/"data/collection-index.json").read_text())
ledger=json.loads((STAGING/"migration/fabaceae-verified-photo-ledger.json").read_text())
owner_path=STAGING/"migration/fabaceae-private-owner-photo-ledger.json"
owner_ledger=json.loads(owner_path.read_text()) if owner_path.is_file() else {}
decisions=json.loads((STAGING/"migration/fabaceae-photo-200-decisions.json").read_text())
audit=json.loads((STAGING/"migration/fabaceae-photo-pass1-summary.json").read_text())
pass2_path=STAGING/"migration/fabaceae-photo-pass2-summary.json"
if pass2_path.is_file():
 current=json.loads(pass2_path.read_text())
 assert current["source_originals_total"]==200
 assert current["originals_physically_byte_verified"]+current["source_originals_held"]==200
 assert current["canonical_source_subtree_sha"]==audit["canonical_source_subtree_sha"]
 assert current["originals_physically_byte_verified"]>=audit["original_photos_byte_archived_in_private_staging"]
 audit={**audit,
    "original_photos_byte_archived_in_private_staging":current["originals_physically_byte_verified"],
    "photos_held_with_documented_reasons":current["source_originals_held"]}
pass3_path=STAGING/"migration/fabaceae-photo-pass3-gbif-summary.json"
if pass3_path.is_file():
 current=json.loads(pass3_path.read_text())
 assert current["source_original_photos_total"]==200
 assert current["original_photos_archived"]+current["source_original_photos_held"]==200
 assert current["source_family_subtree_sha"]==audit["canonical_source_subtree_sha"]
 assert current["original_photos_archived"]>=audit["original_photos_byte_archived_in_private_staging"]
 audit={**audit,
    "original_photos_byte_archived_in_private_staging":current["original_photos_archived"],
    "photos_held_with_documented_reasons":current["source_original_photos_held"]}
assert config["publication"]["enabled"] is False
assert index["authority"]=="STAGING_ONLY" and len(index["entries"])==91
assert audit["original_photos_accounted_for"]==200 and len(decisions)==200
# The verified photo ledger and 200 exact-source decisions are authoritative even as
# later Commons / inaturalist recovery passes add images beyond the pass-3 summary.
assert len({x["source_path"] for x in decisions})==200
assert len(ledger)>=audit["original_photos_byte_archived_in_private_staging"]
assert not (set(ledger)&set(owner_ledger))
assert len(ledger)+len(owner_ledger)+sum(x["status"]=="HOLD" for x in decisions)==200
audit["original_photos_byte_archived_in_private_staging"]=len(ledger)+len(owner_ledger)
audit["photos_held_with_documented_reasons"]=200-len(ledger)-len(owner_ledger)
assert set(ledger)=={r["source_path"] for r in decisions if r["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}
assert set(owner_ledger)=={r["source_path"] for r in decisions if r["status"]=="STAGED_PRIVATE_OWNER_PERMISSION"}
assert set(x["source_path"] for x in decisions)=={x["source_path"] for x in decisions}
assert all(not x.get("publication_approved") for x in ledger.values())
for k,v in ledger.items():
 assert v["evidence"]["license"].startswith(("CC BY","CC0","PUBLIC DOMAIN"))
 assert v["evidence"]["pixel_phash_distance"]<=12
 assert v["evidence"]["creator"] and v["evidence"]["source_page"].startswith("https://")
assert all(x["evidence"].get("public_cc_license_not_inferred") is True and x["private_rights_review_only"] is True for x in owner_ledger.values())
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def to_text(v):
 if isinstance(v,str):return v.strip()
 if isinstance(v,list):return "; ".join(str(x).strip() for x in v if isinstance(x,(str,int,float)))
 return ""
if DEST.exists():shutil.rmtree(DEST)
(DEST/"data/species").mkdir(parents=True)
for name in ("index.html","app.js","styles.css","RUN_FABACEAE_REVIEW.bat"):
 shutil.copyfile(SHELL/"site"/name,DEST/name)
h=(DEST/"index.html").read_text()
h=h.replace("Layout prototype only.</strong> No botanical records or photographs have been transferred to this collection.",
 "Private real-photo review.</strong> All 91 source botanical records are staged; only exact-source CC images or individually owner-authorized private photos appear. Remaining photos are held.")
assert "Private real-photo review." in h
(DEST/"index.html").write_text(h)
(DEST/"data/collection-meta.json").write_text(json.dumps(config,indent=2)+"\n")
(DEST/"data/collection-index.json").write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\n")
photos_by_species={}
for key,rec in {**ledger,**owner_ledger}.items():photos_by_species.setdefault(rec["species_id"],[]).append((key,rec))
total=0
present=[]
for row in index["entries"]:
 card=json.loads((STAGING/row["path"]).read_text())
 assert card["id"]==row["id"] and card["family"]=="Fabaceae"
 morph=card.get("morphology_keys") or {}
 traits=[{"label":k.replace("_"," ").capitalize(),"text":to_text(v)[:950]} for k,v in morph.items() if to_text(v)] if isinstance(morph,dict) else []
 compare=card.get("comparisons") or {}
 confused=compare.get("confused_with") or [] if isinstance(compare,dict) else []
 if isinstance(confused,str):confused=[confused]
 if not isinstance(confused,list):confused=[]
 differences=to_text(compare.get("key_distinctions")) if isinstance(compare,dict) else ""
 order={}
 for i,im in enumerate(card.get("images") or []):
  if isinstance(im,dict):
   file=im.get("file") or ""
   if file.startswith("images/"):
    order[(Path(row["path"]).parent/file).as_posix()]=i
 pairs=sorted(photos_by_species.get(row["id"],[]),key=lambda kv:order.get(kv[0],999))
 verified=[]
 for path,rec in pairs:
  orig=STAGING/path
  assert orig.is_file(),path
  data=orig.read_bytes()
  assert blob(data)==rec["source_git_blob_sha"],path
  rel=f"media/{row['id']}/{len(verified)+1:02d}.jpg"
  out=DEST/rel;out.parent.mkdir(parents=True,exist_ok=True)
  with Image.open(orig) as im:
   img=ImageOps.exif_transpose(im)
   img=img.convert("RGB")
   img.thumbnail((1600,1600),Image.Resampling.LANCZOS)
   img.save(out,"JPEG",quality=83,optimize=True,exif=b"")
  ev=rec["evidence"]
  verified.append({"src":rel,"role":rec["role"] or "Exact-source photo, anatomy review pending",
    "creator":ev["creator"],"license":ev["license"],"license_url":ev["license_url"],
    "source_page":ev["source_page"],"source_page_is_exact":True,
    "noncommercial_only":False,"private_rights_review_only":path in owner_ledger,
    "rights_note":("Direct photographer permission for this private Hays Botany learner. Original iNaturalist photo is all rights reserved; no public CC grant inferred." if path in owner_ledger else ""),
    "modified":"Resized/re-encoded to JPEG and metadata removed; no anatomy arrows",
    "source_blob_sha":rec["source_git_blob_sha"]})
  total+=1
 if verified:present.append(row["id"])
 doc={"id":row["id"],"scientific_name":row["scientific_name"],
   "common_name":row.get("common_name",""),"family":"Fabaceae","genus":row["genus"],
   "look_here_first":to_text(card.get("look_here_first")),
   "key_traits":traits,"lookalikes":{"names":confused[:12],"differences":differences},
   "verified_photos":verified,"media_status":"PRIVATE_MIXED_SOURCE_VERIFIED_CC_AND_OWNER_PERMISSION_NOT_PUBLISHED",
   "source_snapshot_sha":index["source_commit_sha"]}
 (DEST/"data/species"/(row["id"]+".json")).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
assert total==len(ledger)+len(owner_ledger) and len(list((DEST/"data/species").glob("*.json")))==91
assert len(list((DEST/"media").rglob("*.jpg"))) == total if total else not (DEST/"media").exists()
summary={"status":"FABACEAE_REAL_PHOTO_PRIVATE_TEST_NOT_DEPLOYED",
 "species":91,"species_with_verified_photos":len(present),"verified_source_photos_displayed":total,
 "species_without_verified_photos":91-len(present),
 "held_original_photo_files":audit["photos_held_with_documented_reasons"],
 "noncommercial_photo_instances":0,"owner_permission_photo_instances":len(owner_ledger),
 "strict_cc_photo_instances":len(ledger),"source_taxonomy_tree_sha":audit["canonical_source_subtree_sha"],
 "public_pages_enabled":False,
 "exact_source_photo_ids":present}
(DEST/"data/preview-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print("FABACEAE_REAL_PHOTO_SITE",json.dumps({k:v for k,v in summary.items() if k!="exact_source_photo_ids"},sort_keys=True),flush=True)
