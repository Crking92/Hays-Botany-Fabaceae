#!/usr/bin/env python3
"""Verify Fabaceae_004 Zornia images against live photo rights and exact original hashes."""
from __future__ import annotations
import hashlib, io, json, os, time, urllib.request
from pathlib import Path
from PIL import Image

RECORDS = [
 (633215281,347300298,"bcd7c62ba831a40fb9675e078ca6f7ccf0df16ce601cf8fcd6453239b42f72ad","Derek Muschalek","cc-by-nc"),
 (637228725,349329609,"ae46ba431ad8fb6b5be9136c91e9e5716645e02bdb27b2a02911597e168c1b79","Chet Burrier","cc-by"),
 (634685799,348038353,"d5736bf38fe31885c6e2af8abb99edd5b5e68f870194453d020a713ff569d906","George Afghan","cc-by-nc"),
 (647517827,354980648,"1249c7559567179678ad90a02005f4e5092e0ae62bce5402e8ae592b647b467c","Chet Burrier","cc-by"),
 (640523417,351023759,"3ece2b3149c52a819f72843ef6a7179fe0e1229e11caa064618097f8ff4c95b0","Jack Cochran","cc-by-nc"),
]
LICENSES={"cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
          "cc-by-nc":("CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/")}
def get(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyPhotoFirst/1.0 (exact photo and license check)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=30) as res: data=res.read(limit+1)
            if len(data)>limit:raise ValueError("Downloaded source exceeds allowed size")
            return data
        except Exception:
            if attempt==2:raise
            time.sleep(2+attempt)

def main():
    source=Path(os.environ.get("PUBLIC_DIR","shell"))
    staging=Path(os.environ.get("STAGING_DIR","staged"))
    site=json.loads((source/"site/data/collection-meta.json").read_text())
    if site.get("repository_full_name")!="Crking92/Hays-Botany-Fabaceae" or "Fabaceae" not in site.get("family_assignments",[]):
        raise SystemExit("Incorrect family repository")
    if site.get("photo_license_policy",{}).get("noncommercial_educational_use") is not True:
        raise SystemExit("Noncommercial photo publishing is not enabled")
    sid="zornia-bracteata"
    if not (source/"site/data/species"/(sid+".json")).is_file():
        raise SystemExit("Missing public indexed Zornia species")
    existing_source=set()
    existing_hash=set()
    for f in (source/"site/data/species").glob("*.json"):
        for p in json.loads(f.read_text()).get("verified_photos",[]):
            if p.get("source_page"): existing_source.add(p["source_page"])
            if p.get("sha256"): existing_hash.add(p["sha256"])
    out=staging/"photo-intake/approved"/sid
    out.mkdir(parents=True,exist_ok=True)
    report=[]
    for pid,oid,sha,creator,expected_license in RECORDS:
        page=f"https://www.inaturalist.org/photos/{pid}"
        record={"photo_id":pid,"observation_id":oid}
        try:
            if page in existing_source or sha in existing_hash:
                record["status"]="ALREADY_PUBLISHED"
                report.append(record)
                continue
            result=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}",3000000))
            observation=next((x for x in result.get("results",[]) if x.get("id")==oid),None)
            if observation is None: raise ValueError("Original iNaturalist observation missing")
            taxon=(observation.get("taxon") or {}).get("name") or ""
            if taxon.lower().strip()!="zornia bracteata":
                raise ValueError("Source taxon does not match Zornia bracteata: "+taxon)
            photo=next((x for x in observation.get("photos",[]) if x.get("id")==pid),None)
            if photo is None: raise ValueError("Exact photo ID absent from observation")
            code=(photo.get("license_code") or "").lower().replace("_","-")
            if code!=expected_license: raise ValueError("Photo-specific live license changed: "+code)
            credit=(photo.get("attribution") or "").strip()
            if not credit or creator.casefold() not in credit.casefold():
                raise ValueError("Original ZIP photographer not confirmed by live photo: "+credit)
            img=get(f"https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/original.jpg",25*1024*1024)
            if hashlib.sha256(img).hexdigest()!=sha:raise ValueError("Source pixels no longer match original ZIP SHA256")
            with Image.open(io.BytesIO(img)) as picture:
                if picture.format!="JPEG" or picture.width*picture.height>80000000:
                    raise ValueError("Unsupported actual image format or size")
                picture.verify()
            filename=f"inat-{pid}.jpg"
            (out/filename).write_bytes(img)
            lname,lurl=LICENSES[code]
            sidecar={
                "species_id":sid,"photo_file":filename,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
                "rights_approved_for_public":True,"taxon_reviewed":True,
                "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
                "policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
                "review_operator":"Fabaceae_004 source/photo license and hash validation workflow",
                "source_review_evidence":f"Live iNaturalist observation {oid}, exact photo {pid}, photographer '{credit}', photo-specific license {code}; original source bytes match supplied ZIP SHA256 {sha}.",
                "taxon_review_evidence":f"Uploaded Fabaceae_004 Zornia contact sheet was visually reviewed for a plausible yellow fabaceous flower and foliage; live iNaturalist observation {oid} reports Zornia bracteata. Specialist identification remains deferred.",
                "approval_note":"Owner standing photo-first release: exact source rights, photographer, source media bytes and plausible species assignment checked.",
                "creator":credit,"source_page":page,"source_page_is_exact":True,
                "license":lname,"license_url":lurl,"noncommercial_site_use_confirmed":True,
                "role":"General Zornia field photograph; precise diagnostic structures not certified",
                "modifications":"Original source photograph unchanged","sha256":sha
            }
            (out/(filename+".json")).write_text(json.dumps(sidecar,indent=2)+"\n")
            record["status"]="SOURCE_AND_RIGHTS_VERIFIED"
            record["license"]=lname
        except Exception as e:
            record["status"]="HELD"
            record["reason"]=str(e)[:300]
        print(json.dumps(record),flush=True)
        report.append(record)
    Path(os.environ.get("AUDIT_PATH","/tmp/fabaceae_004_audit.json")).write_text(
        json.dumps({"batch":"Fabaceae_004.zip","results":report,"vicia_held_missing_credit_license":2},indent=2)+"\n")
    print("FABACEAE_004_RESULTS",json.dumps({s:sum(x["status"]==s for x in report) for s in ["SOURCE_AND_RIGHTS_VERIFIED","ALREADY_PUBLISHED","HELD"]}),flush=True)

if __name__=="__main__": main()
