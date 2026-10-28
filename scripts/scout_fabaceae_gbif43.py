#!/usr/bin/env python3
"""Read-only targeted GBIF multimedia source/rights/pixel audit for held Fabaceae originals.
No staging writes: the output is a job artifact only until individual provenance checks pass.
"""
import hashlib,io,json,re,sys,time,urllib.request,urllib.error
from pathlib import Path
from collections import Counter
from PIL import Image,ImageOps
import imagehash
SOURCE=Path(sys.argv[1]).resolve()
STAGING=Path(sys.argv[2]).resolve()
OUT=Path(sys.argv[3]).resolve()
records=json.loads((STAGING/"migration/fabaceae-photo-200-decisions.json").read_text())
ledger=json.loads((STAGING/"migration/fabaceae-pinned-source-file-ledger.json").read_text())
assert len(records)==200
assert len(ledger["files"])==491
candidates=[r for r in records if r["status"]=="HOLD" and re.fullmatch(r"https://www.gbif.org/occurrence/\d+",r.get("claimed_source_page",""))]
assert len(candidates)==43, f"Expected 43 source GBIF holds, got {len(candidates)}"
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def phash(b):
    with Image.open(io.BytesIO(b)) as im:return imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
def norm(v):return " ".join(re.findall("[a-z0-9]+",str(v or "").lower()))
def photo_license(v):
    u=str(v or "").strip().lower().replace("http://","https://").rstrip("/")
    m=re.fullmatch(r"https://creativecommons.org/licenses/(by|by-sa)/([234](?:\.\d)?)",u)
    if m:return ("CC BY-SA" if m.group(1)=="by-sa" else "CC BY")+" "+m.group(2),u+"/"
    if re.fullmatch(r"https://creativecommons.org/publicdomain/zero/1(?:\.0)?",u):return "CC0 1.0",u+"/"
    return None,None
def matches(name,card):
    text=norm(name)
    target=norm(card["scientific_name"])
    infra=(" var " in " "+target+" " or " subsp " in " "+target+" ")
    synonyms=[x for x in card.get("synonyms",[]) if isinstance(x,str)]
    for candidate in [card["scientific_name"]]+synonyms:
        c=norm(candidate).split()
        if len(c)<2:continue
        if infra:
            if len(c)>=4 and c[2] in ("var","subsp","ssp") and " ".join(c[:4]) in text:return True
        elif " ".join(c[:2]) in text:return True
    return False
def fetch(url,want_json=False):
    last=None
    for k in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyGBIFScout/1.0 (github.com/Crking92/Hays-Botany-Fabaceae)","Accept":"application/json" if want_json else "image/*"})
            with urllib.request.urlopen(req,timeout=28) as resp:
                if want_json:return json.load(resp)
                b=resp.read(16_000_001)
                if not 2000<len(b)<16_000_001:raise ValueError("IMAGE_TOO_SMALL_OR_LARGE")
                return b
        except urllib.error.HTTPError as e:
            last="HTTP_"+str(e.code)
            if e.code not in (429,503,502,504):break
            time.sleep(2**k+2)
        except Exception as e:
            last=type(e).__name__
            time.sleep(1+k)
    raise RuntimeError(last or "REQUEST_FAILED")
out=[]
for r in candidates:
    sp=r["species_id"]
    p=STAGING/("content/taxa/Fabaceae/"+r["source_path"].split("/")[3]+"/"+sp+"/species.json")
    card=json.loads(p.read_text())
    d={"source_path":r["source_path"],"species_id":sp,"claimed_creator":r.get("claimed_creator",""),"claimed_license":r.get("claimed_license",""),"gbif_occurrence_url":r["claimed_source_page"]}
    try:
        orig=(SOURCE/r["source_path"]).read_bytes()
        if blob(orig)!=r["source_git_blob_sha"]:raise ValueError("ORIGINAL_SHA_NOT_MATCHING")
        oid=int(r["claimed_source_page"].rsplit("/",1)[-1])
        data=fetch(f"https://api.gbif.org/v1/occurrence/{oid}",True)
        d["occurrence_scientific_name"]=data.get("scientificName")
        d["occurrence_verbatim_scientific_name"]=data.get("verbatimScientificName")
        d["occurrence_accepted_name"]=data.get("acceptedScientificName")
        names=[data.get(n) for n in ("scientificName","verbatimScientificName","acceptedScientificName")]
        if not any(matches(n,card) for n in names):
            d.update(status="HOLD_GBIF_TAXON_NOT_EXACT")
        else:
            media=data.get("media") or []
            d["multimedia_records"]=len(media)
            checked=[]
            hits=[]
            for m in media[:12]:
                lic,license_url=photo_license(m.get("license"))
                if not lic:
                    checked.append("MEDIA_LICENSE_NOT_COMPATIBLE")
                    continue
                creator=str(m.get("creator") or m.get("rightsHolder") or "").strip()
                if not creator:
                    checked.append("MEDIA_CREATOR_UNVERIFIABLE")
                    continue
                image_url=str(m.get("identifier") or "")
                if not image_url.startswith("https://"):
                    checked.append("MEDIA_ORIGINAL_URL_MISSING")
                    continue
                try:
                    img=fetch(image_url)
                    dist=int(phash(orig)-phash(img))
                    if dist<=12:hits.append({"creator":creator[:280],"license":lic,"license_url":license_url,
                        "source_page":r["claimed_source_page"],"media_identifier":image_url,
                        "pixel_phash_distance":dist,"source_gbif_occurrence_id":oid,
                        "provenance":"GBIF_CURRENT_MULTIMEDIA_EXACT_SOURCE"})
                    else:checked.append("MEDIA_PIXELS_DIFFER:"+str(dist))
                except Exception as e:checked.append("MEDIA_DOWNLOAD_FAILED:"+str(e)[:60])
            if hits:
                d.update(status="CANDIDATE_SOURCE_AND_PIXEL_VERIFIED",evidence=sorted(hits,key=lambda x:x["pixel_phash_distance"])[0])
            else:d.update(status="HOLD_NO_MATCHING_REUSABLE_GBIF_MULTIMEDIA",checks=checked[:15])
    except Exception as e:
        d.update(status="HOLD_GBIF_SOURCE_API_OR_IMAGE_FAILED",error=str(e)[:160])
    out.append(d)
    time.sleep(1.05)
assert len(out)==43
summary={"source_original_gbif_photo_holds":43,"multimedia_and_pixel_verified_candidates":sum(x["status"]=="CANDIDATE_SOURCE_AND_PIXEL_VERIFIED" for x in out),
         "hold_reasons":dict(Counter(x["status"] for x in out if x["status"]!="CANDIDATE_SOURCE_AND_PIXEL_VERIFIED")),
         "file_changes":0,"site_published":False,"original_hub_unchanged":True}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"fabaceae-gbif43-source-research.json").write_text(json.dumps({"summary":summary,"entries":out},indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_GBIF43_READONLY",json.dumps(summary,sort_keys=True),flush=True)
