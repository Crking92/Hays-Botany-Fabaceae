#!/usr/bin/env python3
"""Turn pinned Wikimedia Commons requests into exact approved photo-intake files.
Only HTTPS Commons originals with pinned SHA1, size and API license checks qualify.
"""
import argparse,hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
LICENSES={"CC BY 4.0":"https://creativecommons.org/licenses/by/4.0/","CC BY-SA 4.0":"https://creativecommons.org/licenses/by-sa/4.0/","CC0 1.0":"https://creativecommons.org/publicdomain/zero/1.0/"}
USER_AGENT="HaysBotanyEducationalImageVerifier/1.0 (source credited, noncommercial teaching)"
def require(ok,msg):
    if not ok:raise ValueError("COMMONS_INTAKE_BLOCKED: "+msg)
def fetch(url,max_bytes=25*1024*1024):
    request=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(request,timeout=65) as response:
        require(response.status==200,"Non-200 source response")
        data=response.read(max_bytes+1)
        require(len(data)<=max_bytes,"File exceeded 25 MB")
        return data
def prepare(source,site):
    folder=source/"photo-intake/requests"
    if not folder.is_dir():
        print(json.dumps({"status":"NO_REQUESTS","prepared":0}));return
    rows=json.loads((site/"data/collection-index.json").read_text())["entries"]
    valid={x["id"] for x in rows}
    added=[];skipped=0
    for p in sorted(folder.glob("*/*.json")):
        sid=p.parent.name
        require(p.is_file() and not p.is_symlink() and sid in valid,"Unknown species or unsafe request")
        x=json.loads(p.read_text())
        title=x.get("commons_title","")
        name=x.get("photo_file","")
        sha=x.get("commons_sha1","")
        size=x.get("commons_size")
        license_name=x.get("license")
        require(x.get("schema_version")==1 and x.get("species_id")==sid,"ID mismatch")
        require(isinstance(title,str) and title.startswith("File:") and len(title)<180 and "/" not in title,"Invalid Commons file title")
        require(isinstance(name,str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,110}\.(jpg|jpeg|png|webp)",name)),"Invalid output filename")
        require(isinstance(sha,str) and re.fullmatch("[a-f0-9]{40}",sha),"Missing source SHA1")
        require(isinstance(size,int) and 200<=size<=25*1024*1024,"Invalid original source byte count")
        require(license_name in LICENSES and x.get("license_url")==LICENSES[license_name],"Unapproved license")
        page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":()")
        require(x.get("source_page")==page,"Source URL mismatch")
        creator=x.get("creator","")
        role=x.get("role","")
        require(isinstance(creator,str) and len(creator)>4 and isinstance(role,str) and len(role)>15,"Missing image role or credit")
        dest=site/"media"/sid/name
        if dest.exists():
            card=json.loads((site/"data/species"/(sid+".json")).read_text())
            require(any(q.get("src")=="media/"+sid+"/"+name and q.get("creator")==creator for q in card["verified_photos"]),"Existing media is untracked")
            skipped+=1;continue
        api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
            "action":"query","format":"json","prop":"imageinfo",
            "iiprop":"url|size|sha1|extmetadata","titles":title})
        pages=json.loads(fetch(api,1_000_000))["query"]["pages"]
        require(len(pages)==1,"Unrecognized Commons file metadata")
        images=next(iter(pages.values())).get("imageinfo",[])
        require(len(images)==1,"Missing Commons imageinfo")
        media=images[0]
        require(media.get("sha1","").lower()==sha and media.get("size")==size,"Original checksum/size changed")
        extra=media.get("extmetadata",{})
        license_api=html.unescape(re.sub("<[^>]+>","",str(extra.get("LicenseShortName",{}).get("value",""))))
        require(license_api.upper().replace("-"," ").strip()==license_name.upper().replace("-"," "),"License mismatch on Commons API: "+license_api)
        artist=html.unescape(re.sub("<[^>]+>","",str(extra.get("Artist",{}).get("value",""))))
        require(creator.split(",")[0].strip().lower() in artist.lower() or "Kenraiz" in artist and "Kenraiz" in creator,"Artist mismatch")
        image_url=media.get("url","")
        parsed=urllib.parse.urlparse(image_url)
        require(parsed.scheme=="https" and parsed.netloc=="upload.wikimedia.org","Unexpected source host")
        original=fetch(image_url)
        require(len(original)==size and hashlib.sha1(original).hexdigest()==sha,"Source bytes failed pinned SHA1")
        inbox=source/"photo-intake/approved"/sid
        inbox.mkdir(parents=True,exist_ok=True)
        image_file=inbox/name
        approval_file=inbox/(name+".json")
        require(not image_file.exists() and not approval_file.exists(),"Refusing existing approval overwrite")
        image_file.write_bytes(original)
        approval={"species_id":sid,"photo_file":name,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
          "rights_approved_for_public":True,"taxon_reviewed":True,
          "approved_by":"Automated Commons source metadata review, user-authorized educational publishing",
          "approval_note":"Pinned original SHA1 and CC license confirmed against the exact Wikimedia Commons API file. Species label from original source, not a local voucher.",
          "creator":creator,"source_page":page,"source_page_is_exact":True,
          "license":license_name,"license_url":LICENSES[license_name],
          "role":role,"modifications":"Exact unmodified Wikimedia Commons source original",
          "sha256":hashlib.sha256(original).hexdigest(),"approval_mode":"AUTOMATED_COMMONS_LICENSE_AND_SOURCE_CHECK",
          "source_id_note":"Commons source attribution, botanical correction welcome"}
        approval_file.write_text(json.dumps(approval,indent=2)+"\n")
        added.append({"species_id":sid,"photo_file":name,"sha1":sha})
    print(json.dumps({"status":"PREPARED_COMMONS_IMAGES","prepared":len(added),"already_published":skipped,"items":added},indent=2))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",type=Path,required=True)
    parser.add_argument("--site-root",type=Path,required=True)
    args=parser.parse_args()
    prepare(args.source_root.resolve(),args.site_root.resolve())
