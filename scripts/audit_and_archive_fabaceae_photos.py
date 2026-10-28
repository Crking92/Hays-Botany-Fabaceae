#!/usr/bin/env python3
"""Conservative, source-exact Fabaceae rights audit and private image archive.
Never publishes media, grants rights, modifies source repo, or invents arrows.
"""
import csv, hashlib, io, json, re, subprocess, sys, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image, ImageOps
import imagehash

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1]).resolve()
STAGING=ROOT/"content/taxa/Fabaceae"
MIGRATION=ROOT/"migration"
inventory=json.loads((MIGRATION/"fabaceae-pinned-source-file-ledger.json").read_text())
census=inventory["census"]
assert len(inventory["files"])==491
assert census["original_photo_files"]==200 and census["metadata_files"]==291
assert subprocess.check_output(["git","-C",str(SOURCE),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==census["source_family_subtree_sha"],"Source subtree changed; stop"
photos=[r for r in inventory["files"] if r["category"]=="SOURCE_IMAGE_ORIGINAL"]
assert len(photos)==200
image_exts={".jpg",".jpeg",".png",".webp"}
assert all(Path(r["path"]).suffix.lower() in image_exts for r in photos)
result=[]
archived={}
generic_by_species=defaultdict(int)
cached={}
class Stripper(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)
def plain(raw):
    p=Stripper();p.feed(str(raw or ""));return " ".join(unescape(" ".join(p.parts)).split())
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def get_json(url):
    for retry in range(2):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany-Fabaceae-SourceAudit/1.0 (educational attribution verification; GitHub Crking92/Hays-Botany-Fabaceae)","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=28) as o:
                return json.load(o)
        except Exception:
            if retry:raise
            time.sleep(1)
def download_image(url):
    req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany-Fabaceae-SourceAudit/1.0 educational license validation"})
    with urllib.request.urlopen(req,timeout=30) as o:
        b=o.read(14_000_000)
    assert len(b)<14_000_000 and len(b)>2000,"Invalid or oversized upstream image"
    return b
def phash(b):
    with Image.open(io.BytesIO(b)) as im:return imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
def norm(s):return re.sub(r"[^a-z0-9]+"," ",str(s).lower()).strip()
def accepted_names(card):
    names=[card["scientific_name"]]
    for synonym in card.get("synonyms",[]) or []:
        if isinstance(synonym,str):names.append(synonym)
    out=set()
    for s in names:
        w=norm(s).split()
        if len(w)>=2:
            out.add(" ".join(w[:2]))
            if len(w)>=4 and w[2] in ("var","subsp","ssp"):out.add(" ".join(w[:4]))
    return out
def taxon_matches(name,card):
    # Infraspecific species cards require matching variety/subspecies, not just parent species.
    target=norm(card["scientific_name"])
    actual=norm(name)
    if not actual:return False
    if " var " in " "+target+" " or " subsp " in " "+target+" ":
        return target in actual
    return any(actual==n or actual.startswith(n+" ") for n in accepted_names(card))
def generic(role):
    z=norm(role)
    keywords=("fruit","pod","leaf","leaves","thorn","flower","floret","bract","inflorescence",
       "seed","spine","stem","hair","rachis","pinna","petiole","branch","bud","bark","node","stipule")
    return not any(k in z for k in keywords)
def license_info(url):
    u=url.lower().replace("http://","https://")
    if re.fullmatch(r"https://creativecommons.org/licenses/by/\d(?:\.\d)?/(?:$|.*)",u):
        return "CC BY",u
    if re.fullmatch(r"https://creativecommons.org/licenses/by-sa/\d(?:\.\d)?/(?:$|.*)",u):
        return "CC BY-SA",u
    if u.startswith("https://creativecommons.org/publicdomain/zero/"):
        return "CC0",u
    if u.startswith("https://creativecommons.org/publicdomain/mark/"):
        return "PUBLIC DOMAIN MARK",u
    return None,None
def common_check(row,card,original):
    source_url=row.get("source_page","").strip()
    if not source_url.startswith("https://commons.wikimedia.org/wiki/File:"):
        return None,"COMMONS_FILE_PAGE_MISSING"
    title=urllib.parse.unquote(source_url.split("/wiki/",1)[-1]).replace("_"," ")
    if not title.startswith("File:"):return None,"COMMONS_EXACT_FILE_UNPROVEN"
    cache_key="commons:"+title
    try:
        if cache_key not in cached:
            qs=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1400","titles":title})
            cached[cache_key]=get_json("https://commons.wikimedia.org/w/api.php?"+qs)
        pages=list(cached[cache_key]["query"]["pages"].values())
        info=pages[0]["imageinfo"][0]
        meta=info.get("extmetadata",{})
        url=plain(meta.get("LicenseUrl",{}).get("value",""))
        label,license_url=license_info(url)
        if not label:return None,"CURRENT_COMMONS_REUSE_LICENSE_NOT_STRICT_CC_OR_PD"
        creator=plain(meta.get("Artist",{}).get("value",""))
        if not creator or norm(creator) in ("unknown","anonymous"):return None,"COMMONS_CREATOR_UNVERIFIABLE"
        # Exact file page is grounded in the source CSV; taxon requires an identifying name
        # in file title or independent verification, never infer from plant shape alone.
        name_text=norm(title)
        if not any(n in name_text for n in accepted_names(card)):
            return None,"COMMONS_FILENAME_TAXON_REVIEW_REQUIRED"
        upstream=download_image(info.get("thumburl") or info["url"])
        dist=phash(original)-phash(upstream)
        if dist>12:return None,"UPSTREAM_COMMONS_PIXELS_NOT_MATCHED"
        return {"creator":creator[:300],"license":label,"license_url":license_url,
            "source_page":source_url,"provenance":"COMMONS_EXACT_IMAGEINFO",
            "pixel_phash_distance":dist,"file_title":title},None
    except Exception as e:return None,"COMMONS_API_OR_IMAGE_RECHECK_FAILED:"+type(e).__name__
def inat_check(row,card,original):
    page=row.get("source_page","").strip()
    m=re.fullmatch(r"https://www.inaturalist.org/photos/(\d+).*",page)
    if not m:return None,"INAT_EXACT_PHOTO_SOURCE_MISSING"
    photo_id=int(m.group(1))
    obs_str=str(row.get("observation_id","") or "").strip()
    if not obs_str.isdigit():return None,"INAT_OBSERVATION_ID_MISSING"
    obs_id=int(obs_str)
    try:
        if obs_id not in cached:
            cached[obs_id]=get_json(f"https://api.inaturalist.org/v1/observations/{obs_id}")
            time.sleep(0.8)
        info=cached[obs_id]
        records=info.get("results",[])
        if len(records)!=1:return None,"INAT_OBSERVATION_NOT_RETURNED"
        obs=records[0]
        if not taxon_matches((obs.get("taxon") or {}).get("name",""),card):
            return None,"INAT_OBSERVATION_TAXON_NOT_EXACT"
        pics=[p for p in (obs.get("photos") or []) if int(p.get("id") or 0)==photo_id]
        if len(pics)!=1:return None,"INAT_PHOTO_ID_NOT_ATTACHED_TO_OBSERVATION"
        p=pics[0]
        code=str(p.get("license_code") or "").lower()
        license_map={"cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
          "cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
          "cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/")}
        if code not in license_map:return None,"CURRENT_PHOTO_LICENSE_NOT_PUBLIC_COMPATIBLE"
        creator=(p.get("attribution") or "").strip()
        if not creator:return None,"INAT_PHOTO_CREATOR_NOT_RETURNED"
        photo_url=p.get("url") or ""
        if not photo_url.startswith("https://"):return None,"INAT_CURRENT_IMAGE_URL_MISSING"
        # Prefer returned photo bytes, with exact photo ID already verified against obs.
        upstream=download_image(photo_url.replace("/square.","/large.").replace("/medium.","/large."))
        dist=phash(original)-phash(upstream)
        if dist>12:return None,"UPSTREAM_INAT_PIXELS_NOT_MATCHED"
        license_name,license_url=license_map[code]
        return {"creator":creator[:300],"license":license_name,"license_url":license_url,
          "source_page":page,"observation_id":obs_id,"photo_id":photo_id,
          "observed_taxon":(obs.get("taxon") or {}).get("name",""),
          "provenance":"INAT_EXACT_OBSERVATION_AND_PHOTO_API",
          "pixel_phash_distance":dist},None
    except Exception as e:return None,"INAT_API_OR_IMAGE_RECHECK_FAILED:"+type(e).__name__

def csv_rows(folder):
    p=folder/"image-sources.csv"
    if not p.is_file():return []
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def row_filename(row):
    for k in ("file_name","file"):
        s=(row.get(k) or "").strip()
        if s and not s.startswith(("http:","https:")):return Path(s).name
    return ""
def role_for(card,fname,row):
    for i in card.get("images",[]) or []:
        if isinstance(i,dict) and Path(str(i.get("file",""))).name==fname:
            return str(i.get("role") or row.get("role") or row.get("diagnostic_role") or "")
    return str(row.get("role") or row.get("diagnostic_role") or "")
for source in sorted(photos,key=lambda r:r["path"]):
    rel=Path(source["path"])
    sp=rel.parts[4]
    family_dir=STAGING/rel.parts[3]/sp
    card=json.loads((family_dir/"species.json").read_text(encoding="utf-8"))
    assert card["id"]==sp and card["family"]=="Fabaceae"
    claimed=[row for row in csv_rows(family_dir) if row_filename(row)==rel.name]
    decision={"source_path":rel.as_posix(),"species_id":sp,"scientific_name":card["scientific_name"],
      "source_git_blob_sha":source["git_blob_sha"],"source_size":source["size_bytes"],
      "source_image_original_retained_in_hub":True}
    if len(claimed)!=1:
        decision.update(status="HOLD",reason="NO_UNIQUE_IMAGE_SOURCE_CSV_ENTRY",matching_csv_rows=len(claimed))
        result.append(decision);continue
    row=claimed[0]
    decision.update(role=role_for(card,rel.name,row),claimed_creator=row.get("creator",""),
      claimed_license=row.get("license",""),claimed_source_page=row.get("source_page",""))
    source_bytes=(SOURCE/rel).read_bytes() if (SOURCE/rel).is_file() else b""
    if not source_bytes or gitsha(source_bytes)!=source["git_blob_sha"]:
        decision.update(status="HOLD",reason="CANONICAL_IMAGE_BLOB_MISSING_OR_HASH_MISMATCH")
        result.append(decision);continue
    url=row.get("source_page","").strip()
    if "commons.wikimedia.org/wiki/File:" in url:
        evidence,reason=common_check(row,card,source_bytes)
    elif "www.inaturalist.org/photos/" in url:
        evidence,reason=inat_check(row,card,source_bytes)
    else:evidence,reason=None,"UPSTREAM_PLATFORM_NOT_FIRST_PASS_VERIFIED"
    if not evidence:
        decision.update(status="HOLD",reason=reason)
        result.append(decision);continue
    if generic(decision["role"]) and generic_by_species[sp]>=2:
        decision.update(status="HOLD",reason="REDUNDANT_GENERIC_VIEW_LIMIT")
        result.append(decision);continue
    try:
        with Image.open(io.BytesIO(source_bytes)) as img:
            img.verify()
    except Exception:
        decision.update(status="HOLD",reason="STAGED_IMAGE_DECODE_FAILED")
        result.append(decision);continue
    dest=ROOT/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(source_bytes)
    assert gitsha(dest.read_bytes())==source["git_blob_sha"]
    if generic(decision["role"]):generic_by_species[sp]+=1
    decision.update(status="STAGED_PRIVATE_PUBLIC_COMPATIBLE",evidence=evidence,
      destination_path=rel.as_posix(),pixel_verified=True,
      publication_approved=False,diagnostic_annotations_verified=False)
    archived[rel.as_posix()]=decision
    result.append(decision)
assert len(result)==200
assert len({x["source_path"] for x in result})==200
assert len(archived)==sum(x["status"].startswith("STAGED") for x in result)
photos_in_destination=[p.relative_to(ROOT).as_posix() for p in STAGING.rglob("*")
  if p.is_file() and p.suffix.lower() in image_exts]
assert set(photos_in_destination)==set(archived),"Untracked image in staging"
summary={"status":"FABACEAE_CONSERVATIVE_FIRST_PASS_PRIVATE_ONLY",
  "original_photos_accounted_for":200,
  "original_photos_byte_archived_in_private_staging":len(archived),
  "photos_held_with_documented_reasons":200-len(archived),
  "species_with_at_least_one_archived_verified_photo":len({v["species_id"] for v in archived.values()}),
  "species_total":91,"held_reason_counts":dict(Counter(x.get("reason") for x in result if x["status"]=="HOLD")),
  "verified_provenance_counts":dict(Counter(v["evidence"]["provenance"] for v in archived.values())),
  "canonical_source_subtree_sha":census["source_family_subtree_sha"],
  "public_site_deployed":False,"owner_public_release_approved":False,
  "source_repository_changed":False,
  "image_rights_recheck_at_release_required":True}
MIGRATION.mkdir(parents=True,exist_ok=True)
(MIGRATION/"fabaceae-photo-200-decisions.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
(MIGRATION/"fabaceae-verified-photo-ledger.json").write_text(json.dumps(archived,indent=2,ensure_ascii=False)+"\n")
(MIGRATION/"fabaceae-photo-pass1-summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_PHOTO_AUDIT",json.dumps(summary,sort_keys=True),flush=True)
