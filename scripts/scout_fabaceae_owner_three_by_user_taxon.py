#!/usr/bin/env python3
"""Read-only recovery of three Calvin King original iNat photos lacking observation IDs.

Search only observations of the known owner, then require exact attached photo ID,
taxon, and source image pixel equivalence. No image bytes are transferred.
"""
import hashlib,io,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageOps
import imagehash

ROOT=Path(sys.argv[1]).resolve()
SRC=Path(sys.argv[2]).resolve()
OUT=Path(sys.argv[3]).resolve()
decisions=json.loads((ROOT/"migration/fabaceae-photo-200-decisions.json").read_text())
owners=json.loads((ROOT/"migration/fabaceae-owner-four-audit.json").read_text())
assert len(owners["entries"])==4
targets=[x for x in decisions if x["status"]=="HOLD" and x.get("claimed_creator")=="Calvin King"]
assert len(targets)==3,len(targets)
def norm(s):return " ".join(re.findall("[a-z0-9]+",str(s or "").lower()))
def sha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def phash(b,c):
 with Image.open(io.BytesIO(b)) as a,Image.open(io.BytesIO(c)) as d:
  return int(imagehash.phash(ImageOps.exif_transpose(a).convert("RGB"))-imagehash.phash(ImageOps.exif_transpose(d).convert("RGB")))
def get(url,mode="json"):
 req=urllib.request.Request(url,headers={"User-Agent":"GlassRootGardenFabaceaeOwner/1.0 (source-photo attribution audit; GitHub Crking92/Hays-Botany-Fabaceae)"})
 with urllib.request.urlopen(req,timeout=30) as resp:
  return json.load(resp) if mode=="json" else resp.read(14_000_001)
known_ids=[x["observation_id"] for x in owners["entries"]]
known=get("https://api.inaturalist.org/v1/observations/"+",".join(str(x) for x in known_ids))
known_results=known.get("results") or []
assert len(known_results)==4
owner_ids={int(x["user"]["id"]) for x in known_results}
assert len(owner_ids)==1, "Owner account identity inconsistent; no guessing"
uid=next(iter(owner_ids))
results=[]
for row in targets:
 pid=int(row["claimed_source_page"].rstrip("/").rsplit("/",1)[-1])
 scientific=row["scientific_name"]
 evidence={"source_path":row["source_path"],"species_id":row["species_id"],
           "claimed_photo_url":row["claimed_source_page"],"photo_id":pid}
 try:
  original=(SRC/row["source_path"]).read_bytes()
  assert sha(original)==row["source_git_blob_sha"]
  found=None
  for page in range(1,4):
   query=urllib.parse.urlencode({"user_id":uid,"taxon_name":scientific,"photos":"true","per_page":200,"page":page})
   response=get("https://api.inaturalist.org/v1/observations?"+query)
   for obs in response.get("results") or []:
    photo=[p for p in obs.get("photos") or [] if int(p.get("id") or 0)==pid]
    if photo:
     found=(obs,photo[0]);break
   if found or len(response.get("results") or [])<200:break
   time.sleep(1.1)
  if not found:raise ValueError("EXACT_PHOTO_NOT_FOUND_IN_OWNER_TAXON_OBSERVATION_SEARCH")
  obs,p=found
  if int(obs["user"]["id"])!=uid:raise ValueError("UNEXPECTED_OBSERVER")
  if not norm((obs.get("taxon") or {}).get("name","")).startswith(" ".join(norm(scientific).split()[:2])):
   raise ValueError("OBSERVATION_CURRENT_TAXON_MISMATCH")
  url=(p.get("url") or "").replace("/square.","/large.").replace("/medium.","/large.")
  if not url.startswith("https://"):raise ValueError("CURRENT_IMAGE_MISSING")
  dist=phash(original,get(url,"bytes"))
  if dist>12:raise ValueError("PHOTO_PIXELS_DIFFER:"+str(dist))
  attribution=str(p.get("attribution") or "")
  if "Calvin King" not in attribution:raise ValueError("PHOTOGRAPHER_ATTRIBUTION_NOT_OWNER")
  evidence.update(status="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY",observation_id=obs["id"],
   observed_taxon=(obs.get("taxon") or {}).get("name"),photo_current_url=url,
   current_license=p.get("license_code"),current_attribution=attribution,
   pixel_phash_distance=dist,photo_observation_link_verified=True,
   public_cc_not_inferred=True)
 except Exception as ex:evidence.update(status="HOLD_NO_EXACT_OWNER_OBSERVATION_MATCH",reason=str(ex)[:140])
 results.append(evidence)
 time.sleep(1.05)
assert len(results)==3
summary={"owner_unlinked_originals_audited":3,"exact_observation_photo_matches":sum(x["status"]=="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY" for x in results),
 "held":sum(x["status"]!="OWNER_PROJECT_SOURCE_VERIFIED_PRIVATE_ONLY" for x in results),
 "no_images_transferred":True,"public_website_unchanged":True}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"fabaceae-owner-three-unlinked-evidence.json").write_text(json.dumps({"summary":summary,"entries":results},indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_OWNER_THREE_SOURCE_SEARCH",json.dumps(summary,sort_keys=True),flush=True)
