#!/usr/bin/env python3
"""Read-only iNaturalist photo-ID -> observation / image license investigation.
No source or image writes. Pages are untrusted; verify resulting observation API records.
"""
import hashlib, io, json, re, sys, time, urllib.error, urllib.request
from collections import Counter
from html import unescape
from pathlib import Path
from PIL import Image, ImageOps
import imagehash

ROOT=Path(sys.argv[1]).resolve()
ORIG=Path(sys.argv[2]).resolve()
OUT=Path(sys.argv[3]).resolve()
records=json.loads((ROOT/"migration/fabaceae-photo-200-decisions.json").read_text())
ledger=json.loads((ROOT/"migration/fabaceae-pinned-source-file-ledger.json").read_text())
assert len(records)==200
target=[r for r in records if r.get("reason")=="INAT_OBSERVATION_ID_MISSING" or
    (r["status"]=="HOLD" and r.get("claimed_creator","").strip() in ("Calvin King","Glass Root Garden"))]
assert len(target)==25,len(target)
assert len({x["source_path"] for x in target})==25
files={r["path"]:r for r in ledger["files"] if r["category"]=="SOURCE_IMAGE_ORIGINAL"}
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def phash(b):
    with Image.open(io.BytesIO(b)) as im:return imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
def norm(s):return " ".join(re.findall(r"[a-z0-9]+",str(s or "").lower()))
def taxon_matches(name,card):
    actual=norm(name)
    target=norm(card["scientific_name"])
    is_infra=" var " in " "+target+" " or " subsp " in " "+target+" "
    for s in [card["scientific_name"]]+[a for a in card.get("synonyms",[]) if isinstance(a,str)]:
        tokens=norm(s).split()
        if len(tokens)<2:continue
        if is_infra:
            if len(tokens)>=4 and tokens[2] in ("var","subsp","ssp") and " ".join(tokens[:4]) in actual:return True
        elif actual==" ".join(tokens[:2]) or actual.startswith(" ".join(tokens[:2])+" "):return True
    return False
def fetch(url,mode="json"):
    last=None
    for i in range(3):
        try:
            headers={"User-Agent":"GlassRootGardenFabaceae/1.0 (photo provenance checks; github.com/Crking92/Hays-Botany-Fabaceae)"}
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=22) as r:
                if mode=="json":return json.load(r)
                data=r.read(10_000_001)
                if mode=="text":return data.decode("utf-8","replace")
                if len(data)>10_000_000:raise ValueError("TOO_LARGE")
                return data
        except Exception as e:
            last=f"{type(e).__name__}:{getattr(e,'code','')}"
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):break
            time.sleep(1+i*2)
    raise RuntimeError(last)
def infer_obs(page,pid):
    # Never trust an HTML observation ID by itself; verify that the target photo
    # actually belongs to that observation through current API results.
    ids=set()
    patterns=[
        r"(?:https?://www\.inaturalist\.org)?/observations/(\d{5,11})",
        r'["\x27]observation_id["\x27]\s*:\s*(\d{5,11})',
        r'(?:data-observation-id|data-observation_id)=["\x27](\d{5,11})',
        r'"observation":\s*{"id":\s*(\d{5,11})',
    ]
    for pat in patterns:
        ids.update(int(x) for x in re.findall(pat,page,re.I))
    return sorted(ids)[:12]
results=[]
for n,row in enumerate(target,1):
    path=row["source_path"]; pidstr=(row.get("claimed_source_page") or "").rstrip("/").split("/")[-1]
    d={"source_path":path,"species_id":row["species_id"],"claimed_photo_page":row.get("claimed_source_page",""),
       "claimed_creator":row.get("claimed_creator",""),"claimed_license":row.get("claimed_license",""),
       "previous_hold":row.get("reason")}
    if not pidstr.isdigit():
        d.update(status="HOLD_NO_EXACT_PHOTO_ID");results.append(d);continue
    pid=int(pidstr);d["photo_id"]=pid
    cardpath=ROOT/("content/taxa/Fabaceae/"+path.split("/")[3]+"/"+row["species_id"]+"/species.json")
    card=json.loads(cardpath.read_text())
    try:
        original=(ORIG/path).read_bytes()
        assert gitsha(original)==row["source_git_blob_sha"]
        assert len(original)==files[path]["size_bytes"]
        html=fetch(row["claimed_source_page"],"text")
        d["photo_page_retrieved"]=True
        observations=infer_obs(html,pid)
        d["html_candidate_observation_ids"]=observations
        matched=None
        for oid in observations:
            try:
                obj=fetch("https://api.inaturalist.org/v1/observations/"+str(oid))
                if len(obj.get("results",[]))!=1:continue
                obs=obj["results"][0]
                photos=[x for x in obs.get("photos",[]) if int(x.get("id") or 0)==pid]
                if len(photos)!=1:continue
                p=photos[0]
                taxon=(obs.get("taxon") or {}).get("name") or ""
                code=str(p.get("license_code") or "").lower()
                creator=str(p.get("attribution") or "").strip()
                d.update(observation_id=oid,observed_taxon=taxon,current_photo_license_code=code,
                         current_photo_creator=creator,photo_attached_to_observation=True,
                         exact_taxon_match=taxon_matches(taxon,card))
                imgurl=p.get("url") or ""
                if imgurl.startswith("https://"):
                    imgurl=imgurl.replace("/square.","/large.").replace("/medium.","/large.")
                    try:d["phash_distance"]=int(phash(original)-phash(fetch(imgurl,"binary")))
                    except Exception as e:d["pixel_match_error"]=str(e)[:90]
                d["photo_current_url"]=imgurl
                matched=True
                break
            except Exception as exc:
                d.setdefault("observation_failures",[]).append(str(exc)[:100])
        if matched:
            code=d.get("current_photo_license_code")
            strict=code in ("cc-by","cc-by-sa","cc0")
            d["strict_public_cc_candidate"]=bool(strict and d.get("exact_taxon_match") and d.get("phash_distance",100)>-1 and d.get("phash_distance",100)<=12 and d.get("current_photo_creator"))
            d["owner_project_use_candidate"]=bool(
                row.get("claimed_creator") in ("Glass Root Garden","Calvin King") and
                d.get("exact_taxon_match") and d.get("phash_distance",100)<=12 and
                d.get("current_photo_creator")
            )
            d["status"]="VERIFIED_PHOTO_OBSERVATION_LINK" if d.get("exact_taxon_match") and d.get("phash_distance",100)<=12 else "HOLD_TAXON_OR_PIXEL_NOT_PROVEN"
        else:d["status"]="HOLD_OBSERVATION_ID_UNRESOLVED"
    except Exception as exc:
        d.update(status="HOLD_SOURCE_OR_PAGE_UNREACHABLE",error=str(exc)[:150])
    results.append(d)
    print("INAT_ID_CHECK",n,len(target),row["species_id"],d["status"],flush=True)
    time.sleep(1.05)
assert len(results)==25
summary={
"source_records_checked":25,
"observation_photo_links_verified":sum(x["status"]=="VERIFIED_PHOTO_OBSERVATION_LINK" for x in results),
"strict_public_cc_candidates":sum(x.get("strict_public_cc_candidate",False) for x in results),
"owner_project_use_candidates":sum(x.get("owner_project_use_candidate",False) for x in results),
"hold_status_counts":dict(Counter(x["status"] for x in results if x["status"]!="VERIFIED_PHOTO_OBSERVATION_LINK")),
"previous_source_images_archived":70,
"photo_files_transferred":0,"public_site_changed":False
}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"fabaceae-inat25-link-audit.json").write_text(json.dumps({"summary":summary,"entries":results},indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_INAT25_SOURCE_SCOUT",json.dumps(summary,sort_keys=True),flush=True)
