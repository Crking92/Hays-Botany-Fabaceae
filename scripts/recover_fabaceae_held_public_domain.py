#!/usr/bin/env python3
"""Recover six specifically checked public-domain Fabaceae archival photographs.

Images and original source rights were reviewed individually on November 3, 2026.
No other historical hold is automatically released by this script.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PDM="https://creativecommons.org/publicdomain/mark/1.0/"
PINS={
"Desmanthus/desmanthus-illinoensis/images/illinoensis-seeds.jpg":{
  "sid":"desmanthus-illinoensis",
  "creator":"Steve Hurst / USDA GRIN",
  "url":"https://commons.wikimedia.org/wiki/File:Desmanthus_illinoensis_seeds.jpg",
  "proof":"Source file explicitly credits Steve Hurst of USDA GRIN and the US federal-government public-domain image license.",
  "basis":"US federal employee work",
  "role":"Five brown Desmanthus illinoensis seeds with a 2 mm scale; diagnostic seed anatomy."
},
"Desmanthus/desmanthus-velutinus/images/velutinus-usda-recon.jpg":{
  "sid":"desmanthus-velutinus",
  "creator":"USDA NRCS",
  "url":"https://commons.wikimedia.org/wiki/File:Desmanthus_velutinus.jpg",
  "proof":"Source file explicitly identifies USDA NRCS and US federal-government public-domain authorship.",
  "basis":"US federal employee work",
  "role":"Flowering branch with pale globose flowers and bipinnate foliage."
},
"Neptunia/neptunia-lutea/images/commons-neptunia-lutea.jpg":{
  "sid":"neptunia-lutea",
  "creator":"Mason Brock (Masebrock)",
  "url":"https://commons.wikimedia.org/wiki/File:Neptunia_lutea.jpg",
  "proof":"Author Mason Brock/Masebrock explicitly released the original image into the public domain on Wikimedia Commons.",
  "basis":"Photographer's public-domain dedication",
  "role":"Yellow spherical flower head with projecting stamens and paired sensitive-looking bipinnate foliage."
},
"Senegalia/senegalia-greggii/images/03-flower-spike.jpg":{
  "sid":"senegalia-greggii",
  "creator":"Sue in az",
  "url":"https://commons.wikimedia.org/wiki/File:Acacia-greggii-flower.jpg",
  "proof":"Photographer Sue in az explicitly released this personally photographed Catclaw Acacia flower photo into the public domain.",
  "basis":"Photographer's public-domain dedication",
  "role":"Creamy cylindrical flower spikes with adjacent small bipinnate leaflets."
},
"Senegalia/senegalia-greggii/images/04-seeds-scale.jpg":{
  "sid":"senegalia-greggii",
  "creator":"Steve Hurst / USDA-NRCS PLANTS Database",
  "url":"https://commons.wikimedia.org/wiki/File:Acgr_001_lhp.jpg",
  "proof":"Original file explicitly identifies Steve Hurst USDA-NRCS PLANTS Database and requests source credit for this public-domain federal work.",
  "basis":"US federal employee work",
  "role":"Six brown seeds of catclaw acacia on a color background with a one-centimeter scale."
},
"Senegalia/senegalia-roemeriana/images/02-flat-pods.jpg":{
  "sid":"senegalia-roemeriana",
  "creator":"Tracey Slotta / USDA ARS",
  "url":"https://commons.wikimedia.org/wiki/File:Acacia_roemeriana_01nsh.jpg",
  "proof":"Source image records fruit of Acacia roemeriana and credits Tracey Slotta at USDA ARS under US federal public-domain terms.",
  "basis":"US federal employee work",
  "role":"Flat curved mature pod with a one-centimeter scale."
},
}
def sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",type=Path,required=True)
    parser.add_argument("--site-root",type=Path,required=True)
    a=parser.parse_args()
    source=a.source_root.resolve(); site=a.site_root.resolve()
    decisions=json.loads((source/"migration/fabaceae-photo-200-decisions.json").read_text())
    by={r["source_path"]:r for r in decisions}
    meta=json.loads((site/"data/collection-meta.json").read_text())
    assert meta["repository_full_name"]=="Crking92/Hays-Botany-Fabaceae"
    report={"audited_candidates":len(PINS),"ready":0,"already_published":0,"installed":0,"held":0,"records":[]}
    with tempfile.TemporaryDirectory(prefix="hays-fabaceae-archival-pd-") as td:
        stage=Path(td)
        for sub,pin in PINS.items():
            sid=pin["sid"]; filename=sub.rsplit("/",1)[-1]
            source_key="content/taxa/Fabaceae/"+sub
            hold_file=source/"migration/private-original-photo-holds"/sub
            card=json.loads((site/"data/species"/(sid+".json")).read_text())
            item={"species_id":sid,"original_image":sub}
            try:
                record=by.get(source_key)
                assert record is not None, "Original catalog entry missing"
                assert record.get("status")=="HOLD", "Original catalog no longer held; manually reconcile"
                assert record.get("claimed_source_page")==pin["url"],"Original exact photo source differs"
                assert hold_file.is_file() and not hold_file.is_symlink(),"Original archived bytes unavailable"
                payload=hold_file.read_bytes()
                assert 200<len(payload)<25*1024*1024,"Original size outside publisher limits"
                original_blob=sha(payload)
                assert original_blob==record["source_git_blob_sha"],"Archived original Git blob changed"
                if any(p.get("source_blob_sha")==original_blob for p in card.get("verified_photos",[])):
                    item["status"]="ALREADY_PUBLISHED"
                    report["already_published"]+=1
                    report["records"].append(item)
                    continue
                fname="archive-pd-"+filename
                dst=stage/"photo-intake/approved"/sid/fname
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes(payload)
                old=record.get("claimed_creator") or ""
                if old:
                    assert pin["creator"].split(" / ")[0].casefold() in old.casefold() or (
                        "usda" in pin["creator"].casefold() and "usda" in old.casefold()
                    ),"Author does not match archival metadata"
                sid_scientific=" ".join(sid.split("-")[:2])
                taxon_alias="Acacia "+sid.split("-")[1] if sid.startswith("senegalia-") else sid_scientific
                details={
                    "species_id":sid,"photo_file":fname,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
                    "rights_approved_for_public":True,"taxon_reviewed":True,
                    "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
                    "policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
                    "review_operator":"ChatGPT original-image visual examination and Commons exact-source rights review 2026-11-03",
                    "source_review_evidence":"November 3, 2026 source inspection: "+pin["proof"]+" Commons exact-image page: "+pin["url"]+"; archival source verified with Git blob "+original_blob+". Rights basis: "+pin["basis"]+".",
                    "taxon_review_evidence":"Archived image was individually viewed on November 3, 2026. Original source labels image "+taxon_alias+"; visible structure: "+pin["role"]+" General species plausibility confirmed; detailed anatomical identification deferred.",
                    "approval_note":"Owner standing photo-first policy: original public-domain work evidenced at exact Commons image source, authentic creator credit preserved; no CC0 license has been invented.",
                    "creator":pin["creator"],"source_page":pin["url"],"source_page_is_exact":True,
                    "license":"Public Domain","license_url":PDM,
                    "role":pin["role"],"modifications":"Archived file reproduced without changes; original copyright dedication or US-federal public-domain terms preserved.",
                    "sha256":hashlib.sha256(payload).hexdigest()
                }
                dst.with_name(fname+".json").write_text(json.dumps(details,ensure_ascii=False,indent=2)+"\n")
                item.update(status="RIGHTS_REVIEWED_READY",original_blob=original_blob,creator=pin["creator"],source_page=pin["url"],license="Public Domain")
                report["ready"]+=1
            except Exception as ex:
                item.update(status="HELD",reason=str(ex)[:500])
                report["held"]+=1
            report["records"].append(item)
        if report["ready"]>0:
            publisher=ROOT/"scripts/publish_approved_family_photos.py"
            for check in (True,False):
                args=[sys.executable,str(publisher),"--source-root",str(stage),"--site-root",str(site)]
                if check:args.append("--check")
                r=subprocess.run(args,text=True,capture_output=True)
                if r.returncode:
                    raise RuntimeError("Existing family publisher refused reviewed batch: "+r.stdout+"\n"+r.stderr)
                if not check:
                    out=json.loads(r.stdout)
                    report["installed"]=out["installed"]
                    assert report["installed"]==report["ready"]
        print("FABACEAE_ARCHIVED_PUBLIC_DOMAIN_PASS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
