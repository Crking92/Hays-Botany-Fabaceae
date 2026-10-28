#!/usr/bin/env python3
"""Read-only source exact verification for 4 owner photographs with known obs IDs."""
import csv, hashlib, io, json, re, sys, time, urllib.request
from pathlib import Path
from PIL import Image,ImageOps
import imagehash
ROOT=Path(sys.argv[1]).resolve()
SOURCE=Path(sys.argv[2]).resolve()
OUT=Path(sys.argv[3]).resolve()
rows=json.loads((ROOT/"migration/fabaceae-photo-200-decisions.json").read_text())
targets=[x for x in rows if x["status"]=="HOLD" and x.get("claimed_creator")=="Glass Root Garden"]
assert len(targets)==4
def norm(s):return " ".join(re.findall("[a-z0-9]+",str(s or "").lower()))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def imagehash_distance(b,c):
 with Image.open(io.BytesIO(b)) as a,Image.open(io.BytesIO(c)) as d:
  return int(imagehash.phash(ImageOps.exif_transpose(a).convert("RGB"))-imagehash.phash(ImageOps.exif_transpose(d).convert("RGB")))
def request(url,want_json=False):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyOwnerProvenance/1.0 (github.com/Crking92/Hays-Botany-Fabaceae)"})
 with urllib.request.urlopen(req,timeout=24) as r:
  return json.load(r) if want_json else r.read(15_000_001)
report=[]
for r in targets:
 info=dict(source_path=r["source_path"],species_id=r["species_id"],photo_page=r["claimed_source_page"])
 folder=ROOT/Path(r["source_path"]).parent.parent
 with (folder/"image-sources.csv").open(encoding="utf-8-sig",newline="") as f:entries=list(csv.DictReader(f))
 matches=[x for x in entries if str(x.get("photo_id",""))==r["claimed_source_page"].rsplit("/",1)[-1] and x.get("observation_id","").isdigit()]
 if len(matches)!=1:
  info.update(status="HOLD_NO_EXACT_OBSERVATION_ID")
  report.append(info);continue
 line=matches[0]
 obs_id=int(line["observation_id"])
 photo_id=int(line["photo_id"])
 info.update(observation_id=obs_id,photo_id=photo_id,source_license_claim=line.get("license",""),
             owner_permission_basis=line.get("rights_basis",""),
             old_source_creator=line.get("creator",""))
 try:
  original=(SOURCE/r["source_path"]).read_bytes()
  if blob(original)!=r["source_git_blob_sha"]:raise ValueError("ORIGINAL_GIT_BLOB_MISMATCH")
  data=request("https://api.inaturalist.org/v1/observations/"+str(obs_id),True)
  if len(data.get("results",[]))!=1:raise ValueError("OBSERVATION_MISSING")
  ob=data["results"][0]
  photos=[x for x in ob.get("photos",[]) if int(x.get("id") or 0)==photo_id]
  if len(photos)!=1:raise ValueError("EXACT_PHOTO_NOT_ATTACHED_TO_OBSERVATION")
  p=photos[0]
  info.update(current_taxon=(ob.get("taxon") or {}).get("name"),current_license=p.get("license_code"),
              current_attribution=p.get("attribution"),photo_observation_link_verified=True)
  tax=norm(info["current_taxon"])
  card=json.loads((folder/"species.json").read_text())
  synonyms=[card["scientific_name"]]+[s for s in card.get("synonyms",[]) if isinstance(s,str)]
  if not any(tax.startswith(" ".join(norm(s).split()[:2])) for s in synonyms):raise ValueError("SPECIES_NOT_MATCHING")
  current_photo=p.get("url") or ""
  if not current_photo.startswith("https://"):raise ValueError("PHOTO_IMAGE_URL_MISSING")
  # Request exact photo id attached to the verified observation.
  current_photo=current_photo.replace("/square.","/large.").replace("/medium.","/large.")
  dist=imagehash_distance(original,request(current_photo))
  info["pixel_phash_distance"]=dist
  if dist>12:raise ValueError("SOURCE_IMAGE_PIXELS_MISMATCH")
  if not p.get("attribution"):raise ValueError("CREATOR_ATTRIBUTION_MISSING")
  if not line.get("rights_basis","").startswith("Direct photo-owner") and "direct photographer grant" not in line.get("license","").lower():
   raise ValueError("OWNER_PERMISSION_DOCUMENTATION_MISSING")
  info.update(status="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY",photo_current_url=current_photo,
              sitewide_public_cc_license_not_inferred=True)
 except Exception as e:info.update(status="HOLD_OWNER_PHOTO_NOT_FULLY_PROVEN",reason=str(e)[:160])
 report.append(info)
 time.sleep(1.1)
assert len(report)==4
summary={"owner_photo_candidates":4,"exact_owner_photos_verified":sum(x["status"]=="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY" for x in report),
         "held":sum(x["status"]!="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY" for x in report),
         "no_images_copied":True,"public_site_published":False}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"fabaceae-owner-four-audit.json").write_text(json.dumps({"summary":summary,"entries":report},indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_OWNER_FOUR_READONLY",json.dumps(summary,sort_keys=True),flush=True)
