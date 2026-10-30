#!/usr/bin/env python3
"""Restore only already migrated, strictly reusable photos to public species galleries."""
import hashlib, json, re, shutil, sys
from collections import Counter
from pathlib import Path
SOURCE=Path(sys.argv[1]); ROOT=Path(sys.argv[2]); SITE=ROOT/"site"
ix_path=SITE/"data/collection-index.json"
ix=json.loads(ix_path.read_text())
assert len(ix["entries"])>0
meta_path=SITE/"data/collection-meta.json"
meta=json.loads(meta_path.read_text())
assert len(ix["entries"])==len(list((SITE/"data/species").glob("*.json")))
media=SITE/"media"
media.mkdir(exist_ok=True)
approved_paths=set()
reasons=Counter(); held={}; catalog={}; count=0; records=0; found_species=0; total_bytes=0
def license_info(p):
    name=str(p.get("license") or "").strip()
    if re.search(r"NC|ND|noncommercial|review|unknown|not verified|private|all rights",name,re.I):return None
    if re.fullmatch(r"CC0(?: 1\.0)?",name,re.I):return ("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/")
    if re.fullmatch(r"Public [Dd]omain(?: \(U\.S\. federal work\))?",name,re.I):
        return ("Public Domain","https://creativecommons.org/publicdomain/mark/1.0/")
    m=re.fullmatch(r"CC BY(-SA)? (2\.0|2\.5|3\.0|4\.0)(?: US)?",name,re.I)
    if m:
        return ("CC BY"+("-SA" if m.group(1) else "")+" "+m.group(2),
                "https://creativecommons.org/licenses/"+("by-sa" if m.group(1) else "by")+"/"+m.group(2)+"/")
    return None
# GBIF multimedia evidence was individually verified in the historical photo
# ledger. Only these exact CC0 creator, source, media and original image bytes.
PINNED_GBIF_CC0={
    "https://www.gbif.org/occurrence/5108100988":{
        "creator":"Nautilus 211","taxon":"Astragalus leptocarpus",
        "file":"images/gbif-manual-5108100988-d4eff7545.jpg",
        "media_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/479347175/original.jpeg",
        "blob_sha":"ff0dc7b5109f49cd8abdc0c3ffd105251e661555"},
    "https://www.gbif.org/occurrence/5140729847":{
        "creator":"Donna H.","taxon":"Astragalus plattensis",
        "file":"images/gbif-manual-5140729847-19b7a5e80.jpg",
        "media_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/494561662/original.jpeg",
        "blob_sha":"c198188a68107d4449ff083422f5d18724564761"},
    "https://www.gbif.org/occurrence/6186158439":{
        "creator":"Vince Hale","taxon":"Dalea hallii",
        "file":"images/library-review014-725ce09df227f6c.jpg",
        "media_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/628316900/original.jpg",
        "blob_sha":"248af4a9ced2d582785f767ace9d8e63faa8724e"},
    "https://www.gbif.org/occurrence/6431822939":{
        "creator":"April Coulon","taxon":"Senna pilosior",
        "file":"images/gbif-first-6431822939-9ca58a139a.jpg",
        "media_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/692204066/original.jpg",
        "blob_sha":"022ecb3f31a5d0fcc2f6af35c0e4c8bace42a61e"},
}
PINNED_INAT_GUIDE={
    "https://www.inaturalist.org/guide_taxa/1557820":{
        "creator":"Alison Northup","taxon":"Senegalia wrightii",
        "file":"images/01-flower-spike.jpg","photo_id":"23060929",
        "media_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/23060929/large.jpeg",
        "blob_sha":"7123904bd721d2f259c44021c829a2b6c63619e4"}
}
PINNED_ARCHIVED_GBIF_BY4={
    "content/taxa/Fabaceae/Amorpha/amorpha-canescens/images/library-review018-bed5a45cbae1533.jpg": "d60af509d07358da4e2dad449e4ba815ce1e033f",
    "content/taxa/Fabaceae/Amorpha/amorpha-roemeriana/images/library-review010-e0bd61424bd6d31.jpg": "407859ed46a297d81a56fe6b2a1dccd1cc3bf110",
    "content/taxa/Fabaceae/Amorpha/amorpha-roemeriana/images/library-review033-9fea63b2fcea81c.jpg": "65e43f477ea8711dc17188a9fed7e4299846d74c",
    "content/taxa/Fabaceae/Astragalus/astragalus-crassicarpus-var-berlandieri/images/library-review013-0120fbc5600d918.jpg": "226e7509029af649badaee0d1526f61bcec28fe5",
    "content/taxa/Fabaceae/Astragalus/astragalus-crassicarpus-var-berlandieri/images/library-review013-e063f53de1c602d.jpg": "c77057b2dd37a64ab42f87f896dace0deb2f74f7",
    "content/taxa/Fabaceae/Astragalus/astragalus-lindheimeri/images/gbif-manual-6184971854-8f0e942ba.jpg": "9c7c9fc2e8f0285911f7babe0f348b1e3d1c08b5",
    "content/taxa/Fabaceae/Cercis/cercis-canadensis-subsp-mexicana/images/library-review012-cb5b46a700292bf.jpg": "76af13a33aea582572ea7a946c86072cf70fbfaf",
    "content/taxa/Fabaceae/Dalea/dalea-multiflora/images/gbif-manual-6188527015-4ad7d4c48.jpg": "24e3f9e52cf39e99916b6879c94d34fbbd09ab56",
    "content/taxa/Fabaceae/Desmodium/desmodium-psilophyllum/images/library-review041-ce8aa6357c8acc4.jpg": "d2ffd5c45394bdfb01c6e2b4e5ca156682a875e0",
    "content/taxa/Fabaceae/Desmodium/desmodium-sessilifolium/images/library-review041-0a6382aefa921e2.jpg": "af4544a5d5a3d1288cf80fa43ccb8ac6d557c9c9",
    "content/taxa/Fabaceae/Desmodium/desmodium-sessilifolium/images/library-review041-4e58fb69521e2aa.jpg": "614f9252491d1f433166d0da53d1220f1e388c0a",
}
# The complete historical audit is read from the already transferred
# source branch. The list above is a narrow per-file publication decision.
ARCHIVED_RIGHTS_AUDIT=json.loads((SOURCE/"migration/fabaceae-verified-photo-ledger.json").read_text())
PINNED_ARCHIVED_INAT_CC={
    "content/taxa/Fabaceae/Desmodium/desmodium-paniculatum/images/inat-312240929.jpg": "87dd7c1a01c173829e1ae203ccd945796e532907",
    "content/taxa/Fabaceae/Galactia/galactia-canescens/images/inat-636282769.jpg": "a6ff6a63bab2a20ca3ead0087d4fce7f9fd10b8a",
    "content/taxa/Fabaceae/Hylodesmum/hylodesmum-nudiflorum/images/inat-196269807.jpg": "7f1a8f9ad59ac78c76ee7fd089532c07df44b93d",
    "content/taxa/Fabaceae/Kummerowia/kummerowia-striata/images/inat-5370736.jpg": "36cb6021014182643b8e99cf95dbbf35367f236b",
    "content/taxa/Fabaceae/Lespedeza/lespedeza-texana/images/inat-272775439.jpg": "5e5386718894f00c9df3dac612c90d2df463b660",
    "content/taxa/Fabaceae/Pediomelum/pediomelum-linearifolium/images/inat-141329355.jpg": "0fe5a6cdfe5502a5684f68a2701e86a658aff864",
    "content/taxa/Fabaceae/Pediomelum/pediomelum-tenuiflorum/images/inat-123056915.jpg": "07a9f74a5d22472eb21c8c773aa65617d0530397",
}
def pinned_inat_cc(p,source_path):
    entry=ARCHIVED_RIGHTS_AUDIT.get(source_path,{})
    ev=entry.get("evidence") or {}
    expected_blob=PINNED_ARCHIVED_INAT_CC[source_path]
    license_name=ev.get("license")
    claimed=p.get("license")
    expected_name="CC BY-SA" if license_name=="CC BY-SA 4.0" else "CC BY"
    photo_id=str(ev.get("photo_id") or "")
    species_id=source_path.split("/")[4]
    if not (
        entry.get("source_path")==source_path and
        entry.get("source_git_blob_sha")==expected_blob and
        entry.get("status")=="STAGED_PRIVATE_PUBLIC_COMPATIBLE" and
        entry.get("species_id")==species_id and
        entry.get("claimed_license")==expected_name and
        claimed==expected_name and
        ev.get("provenance")=="INAT_EXACT_OBSERVATION_AND_PHOTO_API" and
        ev.get("pixel_phash_distance")==0 and
        license_name in ("CC BY 4.0","CC BY-SA 4.0") and
        ev.get("observed_taxon","").lower().replace(" ","-")==species_id and
        p.get("file")=="images/inat-"+photo_id+".jpg" and
        p.get("source_page")=="https://www.inaturalist.org/photos/"+photo_id and
        ev.get("source_page")==p.get("source_page") and
        ev.get("creator")==p.get("creator") and
        ev.get("license_url")=="https://creativecommons.org/licenses/"+(
            "by-sa" if expected_name=="CC BY-SA" else "by")+"/4.0/"
    ):
        return None
    return (p["creator"],p["source_page"],(license_name,ev["license_url"]))
def pinned_gbif_by4(p,source_path):
    if source_path not in PINNED_ARCHIVED_GBIF_BY4:
        return None
    entry=ARCHIVED_RIGHTS_AUDIT.get(source_path,{})
    ev=entry.get("evidence") or {}
    expected_blob=PINNED_ARCHIVED_GBIF_BY4[source_path]
    if not (entry.get("source_path")==source_path and
        entry.get("source_git_blob_sha")==expected_blob and
        entry.get("status")=="STAGED_PRIVATE_PUBLIC_COMPATIBLE" and
        entry.get("claimed_license")=="CC BY" and
        ev.get("license")=="CC BY 4.0" and
        ev.get("provenance")=="GBIF_CURRENT_MULTIMEDIA_EXACT_SOURCE" and
        isinstance(ev.get("pixel_phash_distance"),int) and
        ev["pixel_phash_distance"]<=2 and
        ev.get("source_page")==p.get("source_page") and
        ev.get("media_identifier")==p.get("media_source_url") and
        ev.get("creator")==p.get("creator") and
        p.get("license")=="CC BY" and
        p.get("source_determination") and
        entry.get("species_id")==source_path.split("/")[4]):
        return None
    return (p["creator"],p["source_page"],("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"))
def approved(p,source_path=""):
    if source_path in PINNED_ARCHIVED_INAT_CC:
        result=pinned_inat_cc(p,source_path)
        return (result,None) if result else (None,"photo_specific_public_source_unverified")
    if source_path in PINNED_ARCHIVED_GBIF_BY4:
        approved_original=pinned_gbif_by4(p,source_path)
        return (approved_original,None) if approved_original else (None,"photo_specific_public_source_unverified")
    lic=license_info(p)
    if not lic:return None,"unverified_license_or_restricted"
    creator=str(p.get("creator") or "").strip()
    if not creator or re.search(r"unknown|unverified|resolve|source account",creator,re.I):return None,"creator_unverified"
    source=str(p.get("source_page") or "")
    reuse=str(p.get("public_reuse") or "").lower().strip()
    if source in PINNED_GBIF_CC0:
        expected=PINNED_GBIF_CC0[source]
        taxon=str(p.get("accepted_target") or p.get("source_determination") or "")
        if (creator==expected["creator"] and lic[0]=="CC0 1.0" and
            p.get("file")==expected["file"] and
            p.get("media_source_url")==expected["media_url"] and
            taxon.startswith(expected["taxon"]) and
            str(p.get("gbif_occurrence_id") or p.get("source_observation_id") or "")==
              source.rsplit("/",1)[-1]):
            return (creator,source,lic),None
        return None,"photo_specific_public_source_unverified"
    if source in PINNED_INAT_GUIDE:
        expected=PINNED_INAT_GUIDE[source]
        if (creator==expected["creator"] and lic[0]=="CC BY 4.0" and
            p.get("file")==expected["file"] and
            p.get("media_source_url")==expected["media_url"] and
            str(p.get("source_photo_id") or "")==expected["photo_id"] and
            str(p.get("source_photo_license_code") or "").lower()=="cc-by" and
            str(p.get("source_taxon") or "")==expected["taxon"] and
            reuse=="cc-by"):
            return (creator,source,lic),None
        return None,"photo_specific_public_source_unverified"
    if reuse=="no" or reuse=="false" or "review" in reuse or "private" in reuse or "noncommercial only" in reuse:
        return None,"public_reuse_not_cleared"
    if source.startswith("https://commons.wikimedia.org/wiki/File:"):
        # Two original images have now had their missing authors resolved
        # against the exact Commons file pages in the family source branch.
        author_fixed={
            "https://commons.wikimedia.org/wiki/File:Dalea_aurea.jpg":("Mason Brock (Masebrock)","Public Domain"),
            "https://commons.wikimedia.org/wiki/File:Dalea_compacta_-_Vince_Hale_-_517883110.jpeg":("Vince Hale","CC0 1.0")
        }
        if source in author_fixed and (creator,lic[0])!=author_fixed[source]:
            return None,"creator_unverified"
        # Commons originals have individual creator, exact File: page and
        # versioned CC/CC0 terms above. Historical reuse notes vary between
        # "cc-by", "CC0 1.0", and plain-English attribution instructions.
        # Reject genuine holds rather than requiring one arbitrary note format.
        if re.search(r"review|unverified|reconfirm|verify before|private|not cleared|permission required|noncommercial only|hold",reuse,re.I):
            return None,"public_reuse_flag_unverified"
        return (creator,source,lic),None
    # Exact original iNaturalist photograph independently recorded as cc-by,
    # with photographer, version, photo ID and already archived original bytes.
    if (source=="https://www.inaturalist.org/photos/752610634" and
        creator=="(c) fern Wildtruth, some rights reserved (CC BY)" and
        lic[0]=="CC BY 4.0" and str(p.get("source_photo_id"))=="752610634" and
        str(p.get("source_photo_license_code") or "").lower()=="cc-by" and
        str(p.get("source_taxon"))=="Amorpha fruticosa" and reuse.startswith("yes")):
        return (creator,source,lic),None
    # Exact already-archived individual iNaturalist CC BY photographs:
    # retain fixed photo ID, taxon, photographer, recorded photo license and
    # original bytes; never infer rights from an observation or a creator.
    pinned_inat_ccby={
        "743621173":("Dalea purpurea","(c) Chris Stahl, some rights reserved (CC BY)"),
        "745542712":("Dermatophyllum secundiflorum","(c) mattmsa, some rights reserved (CC BY)"),
        "752965027":("Senna roemeriana","(c) Grant Foster, some rights reserved (CC BY)")
    }
    photo_id=str(p.get("source_photo_id") or "")
    if (photo_id in pinned_inat_ccby and
        source=="https://www.inaturalist.org/photos/"+photo_id and
        (str(p.get("source_taxon")),creator)==pinned_inat_ccby[photo_id] and
        str(p.get("source_photo_license_code") or "").lower()=="cc-by" and
        lic[0]=="CC BY 4.0" and reuse.startswith("yes")):
        return (creator,source,lic),None
    if source.startswith("https://www.inaturalist.org/photos/") and creator=="Glass Root Garden":
        if "Direct license from photographer" in str(p.get("license_basis") or "") and lic[0]=="CC BY 4.0" and reuse=="yes":
            return (creator,source,lic),None
    return None,"photo_specific_public_source_unverified"
for row in ix["entries"]:
    sid,family,genus=row["id"],row["family"],row["genus"]
    assert re.fullmatch(r"[a-z0-9-]+",sid)
    origin=SOURCE/"content/taxa"/family/genus/sid/"species.json"
    assert origin.is_file(),str(origin)
    card=json.loads(origin.read_text())
    assert card["id"]==sid and card["family"]==family and card["genus"]==genus
    target=SITE/"data/species"/(sid+".json")
    published=json.loads(target.read_text())
    assert published["id"]==sid
    photos=[]; blocks=[]
    for n,p in enumerate(card.get("images",[]) if isinstance(card.get("images",[]),list) else []):
        records+=1
        file=str(p.get("file") or "")
        if not re.fullmatch(r"images/[A-Za-z0-9._-]+\.(jpg|jpeg|png|webp)",file,re.I):
            blocks.append({"record":n,"reason":"missing_or_remote_original_file"});continue
        source_path=f"content/taxa/{family}/{genus}/{sid}/{file}"
        ok,reason=approved(p,source_path)
        if not ok:
            blocks.append({"record":n,"reason":reason});continue
        # Historical rights-hold archive does not nest by family. It was
        # already transferred and byte-audited; do not fetch new photos.
        candidates=(SOURCE/"content/taxa"/family/genus/sid/file,
                    SOURCE/"migration/private-original-photo-holds"/genus/sid/file,
                    SOURCE/"migration/private-original-photo-holds"/family/genus/sid/file)
        path=next((x for x in candidates if x.is_file()),None)
        if path is None:
            blocks.append({"record":n,"reason":"archived_photo_bytes_missing"});continue
        content=path.read_bytes()
        suffix=path.suffix.lower()
        valid=(content.startswith(b"\xff\xd8\xff") if suffix in (".jpg",".jpeg") else
               content.startswith(b"\x89PNG\r\n\x1a\n") if suffix==".png" else
               content.startswith(b"RIFF") and content[8:12]==b"WEBP")
        if len(content)<500 or len(content)>25*1024*1024 or not valid:
            blocks.append({"record":n,"reason":"file_signature_or_size_problem"});continue
        sha=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()
        pinned=(PINNED_GBIF_CC0.get(str(p.get("source_page") or "")) or
                PINNED_INAT_GUIDE.get(str(p.get("source_page") or "")))
        if pinned and sha!=pinned["blob_sha"]:
            blocks.append({"record":n,"reason":"pinned_source_original_bytes_mismatch"});continue
        if source_path in PINNED_ARCHIVED_GBIF_BY4 and sha!=PINNED_ARCHIVED_GBIF_BY4[source_path]:
            blocks.append({"record":n,"reason":"pinned_source_original_bytes_mismatch"});continue
        if source_path in PINNED_ARCHIVED_INAT_CC and sha!=PINNED_ARCHIVED_INAT_CC[source_path]:
            blocks.append({"record":n,"reason":"pinned_source_original_bytes_mismatch"});continue
        src="media/"+sid+"/"+path.name
        dest=SITE/src
        if dest.exists():
            assert dest.read_bytes()==content,"Historical photo bytes changed unexpectedly: "+src
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,dest)
            assert dest.read_bytes()==content
        approved_paths.add(dest.resolve())
        creator,source,lic=ok
        photos.append({"src":src,"creator":creator,"source_page":source,"license":lic[0],
                       "license_url":lic[1],"source_blob_sha":sha,
                       "role":str(p.get("role") or "Existing field photograph")[:450],
                       "modified":"Exact archived original photograph; no modification",
                       "noncommercial_only":False,"private_rights_review_only":False,
                       "source_page_is_exact":True})
        count+=1;total_bytes+=len(content)
    for block in blocks:reasons[block["reason"]]+=1
    if blocks:held[sid]=blocks
    published["verified_photos"]=photos
    published["photo_status"]="VERIFIED_EXISTING_CC_GALLERY" if photos else "PHOTOS_HELD_FROM_PUBLIC_GALLERY"
    target.write_text(json.dumps(published,ensure_ascii=False,indent=2)+"\n")
    row["photo_count"]=len(photos)
    row["photo_publication_status"]=published["photo_status"]
    catalog[sid]={"count":len(photos),"first_src":photos[0]["src"] if photos else None}
    found_species+=bool(photos)
assert records==count+sum(reasons.values())
actual_paths={p.resolve() for p in media.rglob("*") if p.is_file()}
assert actual_paths==approved_paths,"Website has unapproved or untracked image files"
ix["site_release_stage"]="PUBLIC_EXISTING_SOURCE_CC_PHOTOS"
ix_path.write_text(json.dumps(ix,ensure_ascii=False,indent=2)+"\n")
meta["site_release_stage"]="PUBLIC_EXISTING_SOURCE_CC_PHOTOS"
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
(SITE/"data/gallery-index.json").write_text(json.dumps({
    "schema_version":1,"status":"ONLY_EXISTING_PUBLIC_RIGHTS_CLEARED_SITE_IMAGES",
    "species":len(catalog),"photo_species":found_species,"photo_count":count,"entries":catalog
},ensure_ascii=False,indent=2)+"\n")
report={"collection":ix["collection_id"],"status":"PASS_EXISTING_ONLY_STRICT_PUBLIC_PHOTO_TRANSFER",
    "species":len(catalog),"source_photo_records":records,"photos_copied_and_eligible":count,
    "species_with_photos":found_species,"held_records":sum(reasons.values()),
    "held_by_reason":dict(reasons),"held_by_species":held,
    "total_source_image_bytes":total_bytes,"new_external_images":0,
    "restricted_media_copied":0,"source_branch_modified":False}
(SITE/"photo-source-migration-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(SITE/"PHOTO_PUBLICATION_SCOPE.md").write_text(
  "# Existing-source photographic publication\n\n"+str(count)+" original photos across "+
  str(found_species)+" species were installed from the existing migration after strict exact-image rights review. "+
  str(sum(reasons.values()))+" image records remain held from public display, with per-species reasons "+
  "in site/photo-source-migration-report.json. Original source files are preserved.\n")
print("SOURCE_ONLY_PHOTO_PASS",json.dumps({k:v for k,v in report.items() if k not in ("held_by_species","held_by_reason")},sort_keys=True),flush=True)
