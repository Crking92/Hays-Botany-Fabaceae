#!/usr/bin/env python3
"""Private exact-source Commons rescue of explicit CC0 / CC BY 3.0 US holdings.

Explicit current Commons license metadata + source SHA + pixel hash + taxon required.
Do not infer public-domain rights merely from a 'Public domain' short name.
"""
import hashlib,io,json,re,subprocess,sys,time,urllib.parse,urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
from PIL import Image,ImageOps
import imagehash

SRC=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
MIG=ROOT/"migration"
o=json.loads((MIG/"fabaceae-pinned-source-file-ledger.json").read_text())
rows=json.loads((MIG/"fabaceae-photo-200-decisions.json").read_text())
existing=json.loads((MIG/"fabaceae-verified-photo-ledger.json").read_text())
assert len(rows)==200 and len(existing)>=70
assert subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD:content/taxa/Fabaceae"],text=True).strip()==o["census"]["source_family_subtree_sha"]
oldpaths={r["path"]:r for r in o["files"] if r["category"]=="SOURCE_IMAGE_ORIGINAL"}
targets=[r for r in rows if r["status"]=="HOLD" and r.get("pass2_commons_recheck_reason","").startswith("CURRENT_COMMONS_CC_LICENSE_UNVERIFIED:cc")]
assert len(targets)==8,len(targets)
class Strip(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def plain(v):
 p=Strip();p.feed(str(v or ""));return " ".join(unescape(" ".join(p.parts)).split())
def norm(v):return " ".join(re.findall(r"[a-z0-9]+",str(v or "").lower()))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()
def phash(b):
 with Image.open(io.BytesIO(b)) as im:return imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
def get(url,mode="image"):
 req=urllib.request.Request(url,headers={"User-Agent":"GlassRootGardenFabaceaeCommons/1.0 (exact-source rights audit; github.com/Crking92/Hays-Botany-Fabaceae)"})
 with urllib.request.urlopen(req,timeout=33) as r:
  if mode=="json":return json.load(r)
  data=r.read(12_000_001)
  assert len(data)>2000 and len(data)<12_000_001
  return data
def taxon_ok(title,card):
 target=norm(card["scientific_name"])
 alias=[card["scientific_name"]]+[s for s in card.get("synonyms",[]) if isinstance(s,str)]
 infra=(" var " in " "+target+" " or " subsp " in " "+target+" ")
 for s in alias:
  t=norm(s).split()
  if len(t)<2:continue
  phrase=(" ".join(t[:4]) if len(t)>=4 and t[2] in ("var","subsp","ssp") else " ".join(t[:2]))
  if infra and len(t)<4:continue
  if phrase in norm(title):return True
 return False
new={}
checks=[]
for r in targets:
 record={"path":r["source_path"],"species_id":r["species_id"]}
 try:
  source=SRC/r["source_path"]
  original=source.read_bytes()
  if len(original)!=oldpaths[r["source_path"]]["size_bytes"] or blob(original)!=r["source_git_blob_sha"]:raise ValueError("BLOB_SHA_MISMATCH")
  page=r.get("claimed_source_page","")
  assert page.startswith("https://commons.wikimedia.org/wiki/File:")
  title=urllib.parse.unquote(page.split("/wiki/",1)[1]).replace("_"," ")
  card=json.loads((ROOT/"content/taxa/Fabaceae"/r["source_path"].split("/")[3]/r["species_id"]/"species.json").read_text())
  if not taxon_ok(title,card):raise ValueError("COMMONS_TAXON_TITLE_MISMATCH")
  q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
                            "iiprop":"url|extmetadata","iiurlwidth":"1400","titles":title})
  result=get("https://commons.wikimedia.org/w/api.php?"+q,"json")
  pageinfo=list(result["query"]["pages"].values())[0]
  if "missing" in pageinfo:raise ValueError("CURRENT_COMMONS_FILE_MISSING")
  info=pageinfo["imageinfo"][0]
  meta=info.get("extmetadata",{})
  label=plain(meta.get("LicenseShortName",{}).get("value","")).lower().strip()
  rawlicense=norm(plain(meta.get("License",{}).get("value","")))
  rawurl=plain(meta.get("LicenseUrl",{}).get("value",""))
  if label=="cc0" and (rawlicense in ("cc zero","cc0","cc zero 1 0") or "cc0" in rawurl.lower()):
   lic,licurl="CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"
  elif label=="cc by 3.0 us" and (rawlicense in ("cc by 3 0 us","cc by 3 0") or "by/3.0/us" in rawurl.lower()):
   lic,licurl="CC BY 3.0 US","https://creativecommons.org/licenses/by/3.0/us/"
  else:raise ValueError("LICENSE_SHORTNAME_AND_LICENSE_CODE_DO_NOT_AGREE:"+label+":"+rawlicense)
  artist=plain(meta.get("Artist",{}).get("value",""))
  if not artist or norm(artist) in ("unknown","unattributed","anonymous"):raise ValueError("ARTIST_UNTRACEABLE")
  matches=[]
  for imageurl in (info.get("thumburl"),info.get("url")):
   if not imageurl or not imageurl.startswith("https://"):continue
   try:
    distance=int(phash(original)-phash(get(imageurl)))
    if distance<=12:matches.append(distance)
   except Exception:pass
  if not matches:raise ValueError("COMMONS_PIXELS_NOT_MATCHED")
  evidence={"creator":artist[:300],"license":lic,"license_url":licurl,
    "source_page":page,"provenance":"COMMONS_EXPLICIT_CC0_OR_US_LICENSE_IMAGEINFO",
    "pixel_phash_distance":min(matches),"file_title":title,
    "current_commons_license_short_name":label,"current_commons_license_field":rawlicense}
  dest=ROOT/r["source_path"]
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(original)
  assert blob(dest.read_bytes())==r["source_git_blob_sha"]
  r.update({"status":"STAGED_PRIVATE_PUBLIC_COMPATIBLE","evidence":evidence,
            "destination_path":r["source_path"],"pixel_verified":True,
            "publication_approved":False,"diagnostic_annotations_verified":False})
  r.pop("reason",None)
  new[r["source_path"]]=r
  record.update(status="ARCHIVED_PRIVATE_VERIFIED",license=lic,creator=artist,pixel_distance=min(matches))
 except Exception as e:
  record.update(status="HOLD",reason=str(e)[:160])
  r["pass4_explicit_license_recheck_reason"]=str(e)[:160]
 checks.append(record)
 time.sleep(0.8)
all_verified={**existing,**new}
assert len(rows)==200 and len({r["source_path"] for r in rows})==200
assert len(all_verified)==sum(r["status"]=="STAGED_PRIVATE_PUBLIC_COMPATIBLE" for r in rows)
assert len(all_verified)+sum(r["status"]=="HOLD" for r in rows)==200
actual={f.relative_to(ROOT).as_posix() for f in (ROOT/"content/taxa/Fabaceae").rglob("*")
 if f.is_file() and f.suffix.lower() in (".jpg",".jpeg",".png",".webp")}
assert actual==set(all_verified),f"Unexpected image content: {actual^set(all_verified)}"
summary={"original_source_photos":200,"previous_archived":len(existing),
 "additional_explicit_CC0_CC_BY_US_photos":len(new),"archived":len(all_verified),
 "held":200-len(all_verified),"photo_species":len({r["species_id"] for r in all_verified.values()}),
 "source_held_image_checks":len(targets),"held_check_reasons":dict(Counter(x.get("reason") for x in checks if x["status"]=="HOLD")),
 "canonical_source_tree_unchanged":True,"public_deployment":False}
(MIG/"fabaceae-verified-photo-ledger.json").write_text(json.dumps(all_verified,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-photo-200-decisions.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False)+"\n")
(MIG/"fabaceae-commons-explicit-cc0-us-pass4.json").write_text(json.dumps({"summary":summary,"individual_checks":checks},indent=2,ensure_ascii=False)+"\n")
print("FABACEAE_COMMONS_LICENSE_PASS4",json.dumps(summary,sort_keys=True),flush=True)
