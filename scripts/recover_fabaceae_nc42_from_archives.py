#!/usr/bin/env python3
"""Re-audit the 42 historic Fabaceae CC BY-NC photo holds using exact observation records.
Safe publication requires a source-backed photo ID, original archived bytes, species
identity, individually verified creator/license and matching source-image pixels.
Incomplete evidence remains held in a machine-readable report.
"""
import csv,datetime,hashlib,html,io,json,re,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1];SOURCE=Path(sys.argv[1]).resolve();SITE=ROOT/"site"
LEDGER=SOURCE/"migration/fabaceae-photo-200-decisions.json"
REPORT=ROOT/"workflow/fabaceae-nc42-recovery-result.json"
LICENSES={"cc-by-nc":("CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/"),
          "cc-by-nc-sa":("CC BY-NC-SA 4.0","https://creativecommons.org/licenses/by-nc-sa/4.0/")}
def request(url,as_json=True):
    assert url.startswith("https://"),"source must be HTTPS"
    last=None
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyFabaceaeArchiveNC42/1.0","Accept":"application/json" if as_json else "image/*"})
            with urllib.request.urlopen(req,timeout=28) as r:
                if r.status!=200:raise RuntimeError("bad HTTP code "+str(r.status))
                b=r.read(22*1024*1024)
                return json.loads(b) if as_json else b
        except Exception as exc:
            last=exc;time.sleep(1+i*3)
    raise RuntimeError("exact source inaccessible "+str(last)[:180])
def digest(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def dhash(b):
    with Image.open(io.BytesIO(b)) as im:
        a=list(ImageOps.exif_transpose(im).convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return sum(1<<k for k in range(64) if a[(k//8)*9+k%8]>a[(k//8)*9+k%8+1])
def display_name(s):
    s=html.unescape(re.sub(r"<[^>]*>"," ",str(s or "")))
    s=re.sub(r"^(?:\(c\)|©)\s*","",s.strip(),flags=re.I)
    s=re.split(r",?\s*(?:some rights reserved|uploaded by|no rights reserved)\b",s,flags=re.I)[0]
    return re.sub(r"\s+"," ",s).strip(" ,;.")
def canon_name(s):
    return display_name(s).casefold()
def check_name(a,b):
    a=canon_name(a);b=canon_name(b)
    return bool(a and b and (a in b or b in a))
def source_row(row,photo_id):
    # Original first-party CSV, not migrated summary with missing observation links.
    file=SOURCE/Path(row["source_path"]).parent.parent/"image-sources.csv"
    entry=None
    if file.is_file():
        with file.open(encoding="utf-8-sig",newline="") as fh:
            records=list(csv.DictReader(fh))
        matches=[r for r in records if r.get("file_name")==Path(row["source_path"]).name]
        if len(matches)==1:entry=matches[0]
    if entry and str(entry.get("observation_id") or "").isdigit() and str(entry.get("photo_id") or "").isdigit():
        assert int(entry["photo_id"])==photo_id,"CSV photo ID differs from source"
        return int(entry["observation_id"]),entry
    # Some original cards keep observation IDs only in their embedded image references.
    card=SOURCE/Path(row["source_path"]).parent.parent/"species.json"
    if card.is_file():
        data=json.loads(card.read_text())
        matches=[x for x in data.get("images",[]) if (x.get("file") or "").endswith("/"+Path(row["source_path"]).name)
                 and str(x.get("photo_id") or "").isdigit() and int(x["photo_id"])==photo_id and
                 str(x.get("observation_id") or "").isdigit()]
        if len(matches)==1:return int(matches[0]["observation_id"]),matches[0]
    raise ValueError("No preserved exact observation ID for image in source CSV or species card")
def run():
    raw=json.loads(LEDGER.read_text())
    rows=[r for r in raw if r.get("status")=="HOLD" and r.get("reason")=="CURRENT_PHOTO_LICENSE_NOT_PUBLIC_COMPATIBLE"]
    assert len(rows)==42,"Expected precisely 42 original licensing-hold records, not changed list"
    meta=json.loads((SITE/"data/collection-meta.json").read_text())
    assert meta["repository_full_name"]=="Crking92/Hays-Botany-Fabaceae"
    assert meta["photo_license_policy"]["noncommercial_educational_use"] is True
    published={p.get("source_blob_sha") for path in (SITE/"data/species").glob("*.json")
         for p in json.loads(path.read_text()).get("verified_photos",[])}
    report={"batch":"historical Fabaceae 42 previously held individual iNaturalist photos","candidates":42,"published":0,
       "already_published":0,"held":0,"verified_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"records":[]}
    with tempfile.TemporaryDirectory(prefix="fabaceae-nc42-originals-") as td:
        temp=Path(td)
        for row in rows:
            sid=row["species_id"];path=row["source_path"]
            rec={"species_id":sid,"source_path":path}
            try:
                m=re.fullmatch(r"https://www.inaturalist.org/photos/(\d+)",row.get("claimed_source_page") or "")
                assert m,"no exact original iNaturalist photo source"
                pid=int(m.group(1));rec["photo_id"]=pid
                original=SOURCE/path
                assert original.is_file(),"original photo file absent"
                payload=original.read_bytes()
                assert 200<len(payload)<25*1024*1024,"original outside file-size limit"
                gitsha=digest(payload)
                assert gitsha==row["source_git_blob_sha"],"original photo Git blob differs from original ledger"
                if gitsha in published:
                    report["already_published"]+=1;rec["status"]="ALREADY_PUBLISHED";report["records"].append(rec);continue
                oid,source_entry=source_row(row,pid)
                obs=request(f"https://api.inaturalist.org/v1/observations/{oid}")
                results=obs.get("results") or []
                assert len(results)==1 and results[0].get("id")==oid,"observation not found or mismatched"
                observation=results[0]
                taxon=(observation.get("taxon") or {}).get("name") or ""
                expected=" ".join((row.get("scientific_name") or "").split()[:2])
                assert taxon.startswith(expected) and len(expected.split())==2,"source observation taxon differs: "+taxon+" vs "+expected
                photos=[p for p in (observation.get("photos") or []) if int(p.get("id") or 0)==pid]
                assert len(photos)==1,"original photo ID no longer inside stated observation"
                photo=photos[0]
                license_code=str(photo.get("license_code") or "").lower().strip()
                assert license_code in LICENSES,"photo-specific license not permitted now: "+license_code
                old_license=(row.get("claimed_license") or "").lower().replace(" ","").replace("-4.0","")
                assert "by-nc" in old_license and "nd" not in old_license,"original license claim incompatible"
                if license_code=="cc-by-nc-sa":assert "sa" in old_license
                else:assert "sa" not in old_license
                credit=photo.get("attribution") or ""
                assert check_name(row.get("claimed_creator"),credit),"photo creator differs from archived credit: "+credit
                remote_url=photo.get("large_url") or photo.get("url") or ""
                assert remote_url.startswith("https://"),"current image URL is not HTTPS"
                distance=(dhash(payload)^dhash(request(remote_url,False))).bit_count()
                assert distance<=12,"original archive image does not resemble current same-photo pixels: "+str(distance)
                licensed,license_url=LICENSES[license_code]
                filename="historical-nc-"+re.sub(r"[^a-z0-9._-]","-",Path(path).name.lower())
                dest=temp/"photo-intake/approved"/sid/filename
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(payload)
                creator=display_name(credit)
                assert creator,"no verified photographer"
                role=row.get("role") or source_entry.get("role") or "General species habit and field recognition"
                evidence=f"Exact archived photo {pid} at observation {oid} with current source taxon {taxon}; original SHA {gitsha}; current photo license {license_code} and photographer {credit}; source-photo visual fingerprint distance {distance}; verified {report['verified_at']}."
                taxon_review=f"Photo reviewed in historical family source archive as {sid}; current individual iNaturalist observation {oid} identifies {taxon}; original and current media visually match (difference {distance}); specialist morphological determination deferred."
                sidecar={
                    "species_id":sid,"photo_file":filename,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
                    "rights_approved_for_public":True,"taxon_reviewed":True,
                    "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY","policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
                    "review_operator":"Hays Botany historical source and current iNaturalist photo check",
                    "source_review_evidence":evidence,"taxon_review_evidence":taxon_review,
                    "approval_note":"Owner standing photo-first release: exact archive and current individual-photo license/creator/species/source match; credit and noncommercial restrictions carried to gallery.",
                    "creator":creator,"source_page":row["claimed_source_page"],"source_page_is_exact":True,
                    "license":licensed,"license_url":license_url,"noncommercial_site_use_confirmed":True,
                    "role":role,"modifications":"Historical archived photo reproduced unchanged; not independently edited.",
                    "sha256":hashlib.sha256(payload).hexdigest()}
                dest.with_name(filename+".json").write_text(json.dumps(sidecar,indent=2,ensure_ascii=False)+"\n")
                rec.update(status="RIGHTS_VERIFIED_READY",creator=creator,license=licensed,observation_id=oid,source_blob_sha=gitsha,dhash_distance=distance)
            except Exception as e:
                rec.update(status="HELD",reason=str(e)[:450])
                report["held"]+=1
            report["records"].append(rec)
        eligible=sum(r["status"]=="RIGHTS_VERIFIED_READY" for r in report["records"])
        if eligible:
            pub=ROOT/"scripts/publish_approved_family_photos.py"
            args=[sys.executable,str(pub),"--source-root",str(temp),"--site-root",str(SITE)]
            for suffix in (["--check"],[]):
                result=subprocess.run(args+suffix,capture_output=True,text=True)
                if result.returncode:raise RuntimeError("Publisher blocked batch: "+result.stdout+result.stderr)
                if not suffix:report["published"]=json.loads(result.stdout)["installed"]
            assert report["published"]==eligible
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        from collections import Counter
        print("FABACEAE_NC42_AUDIT",json.dumps({"published":report["published"],"held":report["held"],"already":report["already_published"],
           "hold_reasons":dict(Counter(r.get("reason") for r in report["records"] if r["status"]=="HELD"))},ensure_ascii=False),flush=True)
if __name__=="__main__":run()
