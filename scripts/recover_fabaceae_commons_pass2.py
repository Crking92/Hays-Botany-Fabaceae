#!/usr/bin/env python3
"""Add only byte- and current-license-verified Commons originals to private Fabaceae staging.

Second pass over held Commons photo files, not a reinterpretation of old CSV claims.
Existing pass-1 approvals remain intact; failure to access Commons never revokes a verified image.
"""
import csv, hashlib, io, json, re, subprocess, sys, time, urllib.parse, urllib.request, urllib.error
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image, ImageOps
import imagehash

SRC=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
MIG=ROOT/"migration"
files=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
rows=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
prior=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
old=json.loads((MIG/"fabaceae-photo-pass1-summary.json").read_text())
assert len(rows)==200 and old["original_photos_accounted_for"]==200
assert files["census"]["source_family_subtree_sha"]==old["canonical_source_subtree_sha"]
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==old["canonical_source_subtree_sha"]
assert {r["source_path"] for r in rows}=={r["path"] for r in files["files"] if r["category"]=="SOURCE_IMAGE_ORIGINAL"}
assert set(prior)=={r["source_path"] for r in rows if r["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}
originals={r["path"]:r for r in files["files"] if r["category"]=="SOURCE_IMAGE_ORIGINAL"}
all_species={p.parent.name:p for p in (ROOT/"content/taxa/Fabaceae").glob("*/*/species.json")}
updated=[]
new={}
failures=[]
targeted=0

def norm(s):return " ".join(re.findall(r"[a-z0-9]+",str(s).lower()))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def phash(b):
    with Image.open(io.BytesIO(b)) as im:return imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
class Text(HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_data(self,v):self.items.append(v)
def plain(s):
    t=Text();t.feed(str(s or ""));return " ".join(unescape(" ".join(t.items)).split())
def licensed(url):
    u=str(url or "").lower().strip().replace("http://","https://").rstrip("/")
    m=re.fullmatch(r"https://creativecommons.org/licenses/(by|by-sa)/([234](?:\.\d)?)",u)
    if m:
        label="CC BY-SA" if m.group(1)=="by-sa" else "CC BY"
        return label+" "+m.group(2),u+"/"
    m=re.fullmatch(r"https://creativecommons.org/publicdomain/zero/(1(?:\.0)?)",u)
    if m:return "CC0 1.0",u+"/"
    return None,None

def fetch(url,as_json=False):
    last=None
    for retry in range(4):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"HaysBotanyFabaceae/1.1 (license-check; github.com/Crking92/Hays-Botany-Fabaceae)",
                "Accept":"application/json" if as_json else "image/avif,image/webp,image/*,*/*;q=0.8"
            })
            with urllib.request.urlopen(req,timeout=35) as response:
                if as_json:return json.load(response)
                b=response.read(18_000_001)
                if not 2000<len(b)<18_000_001:raise ValueError("image file empty/oversized")
                return b
        except urllib.error.HTTPError as exc:
            last=f"HTTP_{exc.code}"
            if exc.code not in (408,429,500,502,503,504):break
            delay=min(14,2**retry+2)
            try:delay=min(18,max(delay,float(exc.headers.get("Retry-After","0"))))
            except (ValueError,TypeError):pass
            time.sleep(delay)
        except Exception as exc:
            last=type(exc).__name__
            time.sleep(1.0+retry)
    raise RuntimeError(last or "UPSTREAM_FETCH_FAILED")

def taxon_ok(title,card):
    label=norm(title)
    scientific=card["scientific_name"]
    names=[scientific]+[s for s in (card.get("synonyms") or []) if isinstance(s,str)]
    # Never promote infraspecific records based on the parent species alone.
    infra=(" var " in " "+norm(scientific)+" " or " subsp " in " "+norm(scientific)+" ")
    for name in names:
        bits=norm(name).split()
        if len(bits)<2:continue
        phrase=" ".join(bits[:2])
        if infra:
            if len(bits)>=4 and bits[2] in ("var","subsp","ssp") and " ".join(bits[:4]) in label:return True
        else:
            if phrase in label:return True
    return False

def candidate(row):
    path=row["source_path"]
    card=json.loads(all_species[row["species_id"]].read_text())
    source_url=row.get("claimed_source_page") or ""
    if not source_url.startswith("https://commons.wikimedia.org/wiki/File:"):
        return None,"COMMONS_EXACT_FILE_URL_NOT_GROUNDED"
    title=urllib.parse.unquote(source_url.split("/wiki/",1)[-1]).replace("_"," ")
    if not title.startswith("File:"):return None,"COMMONS_FILE_TITLE_MISSING"
    if not taxon_ok(title,card):return None,"COMMONS_TAXON_NOT_PROVEN_BY_TITLE_OR_SYNONYM"
    orig=(SRC/path).read_bytes()
    if blob(orig)!=row["source_git_blob_sha"] or len(orig)!=originals[path]["size_bytes"]:
        return None,"ORIGINAL_BLOB_HASH_OR_SIZE_MISMATCH"
    try:
        query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
                                     "iiprop":"url|extmetadata","iiurlwidth":"1200",
                                     "titles":title})
        data=fetch("https://commons.wikimedia.org/w/api.php?"+query,True)
        p=list(data["query"]["pages"].values())[0]
        if "missing" in p:return None,"CURRENT_COMMONS_FILE_NOT_FOUND"
        info=p["imageinfo"][0]
        meta=info.get("extmetadata",{})
        licraw=plain(meta.get("LicenseUrl",{}).get("value",""))
        label,lic=licensed(licraw)
        if not lic:
            return None,"CURRENT_COMMONS_CC_LICENSE_UNVERIFIED:"+norm(plain(meta.get("LicenseShortName",{}).get("value","")))[:50]
        creator=plain(meta.get("Artist",{}).get("value",""))
        if not creator or norm(creator) in ("unknown","anonymous","unattributed"):
            return None,"CURRENT_COMMONS_CREATOR_UNVERIFIED"
        images=[info.get("thumburl"),info.get("url")]
        pixels=None;fails=[]
        for link in images:
            if not link or not link.startswith("https://"):continue
            try:
                other=fetch(link,False)
                distance=int(phash(orig)-phash(other))
                if distance<=12:
                    pixels=distance
                    break
                fails.append("PHASH_"+str(distance))
            except Exception as exc:
                fails.append(str(exc)[:60])
        if pixels is None:return None,"CURRENT_COMMONS_IMAGE_UNMATCHED:"+",".join(fails)[:90]
        return {"creator":creator[:300],"license":label,"license_url":lic,"source_page":source_url,
                "provenance":"COMMONS_EXACT_IMAGEINFO_PASS2","file_title":title,
                "pixel_phash_distance":pixels,"current_license_original":licraw},None
    except Exception as exc:
        return None,"COMMONS_RECHECK_FAILED:"+str(exc)[:110]

for row in rows:
    row=dict(row)
    if row["status"]!="HOLD" or "commons.wikimedia.org/wiki/File:" not in str(row.get("claimed_source_page","")):
        updated.append(row)
        continue
    targeted+=1
    ev,reason=candidate(row)
    if ev:
        source=row["source_path"]
        d=ROOT/source
        d.parent.mkdir(parents=True,exist_ok=True)
        b=(SRC/source).read_bytes()
        d.write_bytes(b)
        assert blob(d.read_bytes())==row["source_git_blob_sha"]
        row.update(status="STAGED_PRIVATE_PUBLIC_COMPATIBLE",
                  evidence=ev,destination_path=source,
                  pixel_verified=True,publication_approved=False,
                  diagnostic_annotations_verified=False)
        row.pop("reason",None)
        new[source]=row
    else:
        row["pass2_commons_recheck_reason"]=reason
        failures.append({"source_path":row["source_path"],"species_id":row["species_id"],"reason":reason})
    updated.append(row)
    time.sleep(1.4)

merged={**prior,**new}
assert len(updated)==200 and len({x["source_path"] for x in updated})==200
assert len(merged)==sum(x["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE" for x in updated)
assert set(merged)=={x["source_path"] for x in updated if x["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE"}
assert all(not x.get("publication_approved") for x in merged.values())
actual={p.relative_to(ROOT).as_posix() for p in (ROOT/"content/taxa/Fabaceae").rglob("*")
        if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".webp",".png")}
assert actual==set(merged),f"Unexpected physical images: {actual^set(merged)}"
summary={
  "status":"FABACEAE_COMMONS_SECOND_PASS_PRIVATE_ONLY_NOT_PUBLISHED",
  "source_originals_total":200,
  "originals_physically_byte_verified":len(merged),
  "source_originals_held":200-len(merged),
  "originals_newly_verified_in_commons_pass2":len(new),
  "source_photo_species_with_verified_archives":len({x["species_id"] for x in merged.values()}),
  "species_total":91,
  "commons_held_records_rechecked":targeted,
  "commons_pass2_hold_reasons":dict(Counter(x["reason"] for x in failures)),
  "remaining_original_holds_by_first_pass_reason":dict(Counter(x.get("reason") for x in updated if x["status"]=="HOLD")),
  "canonical_source_subtree_sha":old["canonical_source_subtree_sha"],
  "public_pages_deployed":False,"main_hub_changed":False,
  "manual_field_anatomy_approved":False
}
(MIG/"fabaceae-photo-200-decisions.json").write_text(json.dumps(updated,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-verified-photo-ledger.json").write_text(json.dumps(merged,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-commons-pass2-report.json").write_text(json.dumps({"summary":summary,"new_files":list(new),"held_checks":failures},indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-photo-pass2-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print("FABACEAE_COMMONS_PASS2",json.dumps(summary,sort_keys=True),flush=True)
