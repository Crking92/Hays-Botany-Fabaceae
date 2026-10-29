#!/usr/bin/env python3
"""Browser QA for nondeployed Fabaceae family learner, desktop and phone."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
OUT=ROOT/"qa-report/fabaceae-photo-site"
OUT.mkdir(parents=True,exist_ok=True)
summary=json.loads((DIST/"data/preview-summary.json").read_text())
index=json.loads((DIST/"data/collection-index.json").read_text())
assert summary["species"]==len(index["entries"])==91
assert summary["verified_source_photos_displayed"]>=0
assert summary["noncommercial_photo_instances"]==0
assert not summary["public_pages_enabled"]
assert len(summary["exact_source_photo_ids"])==summary["species_with_verified_photos"]
for row in index["entries"]:
  doc=json.loads((DIST/"data/species"/(row["id"]+".json")).read_text())
  assert doc["id"]==row["id"]
  for photo in doc["verified_photos"]:
    assert (DIST/photo["src"]).is_file()
    assert photo["creator"]
    if photo.get("private_rights_review_only"):
      assert photo["license_url"]=="" and "all rights reserved" in photo["license"]
      assert "no public CC grant" in photo.get("rights_note","")
    else:
      assert photo["license_url"].startswith("https://creativecommons.org/")
    assert photo["source_page"].startswith("https://")
    assert photo["noncommercial_only"] is False
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 for name,viewport,ismobile in [
   ("desktop",{"width":1440,"height":950},False),
   ("mobile",{"width":390,"height":844},True)]:
   pg=browser.new_page(viewport=viewport,device_scale_factor=1,is_mobile=ismobile,has_touch=ismobile)
   errors=[]
   pg.on("pageerror",lambda ex:errors.append(str(ex)))
   pg.goto("http://127.0.0.1:8768/?species=senegalia-greggii",wait_until="networkidle")
   pg.locator("#species-count").wait_for()
   assert pg.locator("#species-count").inner_text()=="91"
   assert "Fabaceae" in pg.locator("#collection-title").inner_text()
   assert pg.locator("#results button").count()==91
   if summary["exact_source_photo_ids"]:
      which=summary["exact_source_photo_ids"][0]
      pg.goto("http://127.0.0.1:8768/?species="+which,wait_until="networkidle")
      imgs=pg.locator(".gallery-photo img")
      imgs.first.wait_for()
      doc=json.loads((DIST/"data/species"/(which+".json")).read_text())
      assert imgs.count()==len(doc["verified_photos"])
      assert all(imgs.nth(i).evaluate("(e)=>e.complete && e.naturalWidth>0") for i in range(imgs.count()))
      assert pg.locator(".gallery-photo a",has_text="Photo source").count()==len(doc["verified_photos"])
      assert pg.locator(".gallery-photo a",has_text="License").count()==sum(bool(p["license_url"]) for p in doc["verified_photos"])
      assert pg.locator(".photo-nc").count()==0
      pg.screenshot(path=str(OUT/f"fabaceae-verified-gallery-{name}.png"),full_page=True)
   else:
      assert "Photographs for this species are held" in pg.locator("#detail").inner_text()
      pg.screenshot(path=str(OUT/f"fabaceae-no-cleared-photos-{name}.png"),full_page=True)
   if summary.get("owner_permission_photo_instances",0):
      pg.goto("http://127.0.0.1:8768/?species=dalea-enneandra",wait_until="networkidle")
      assert pg.locator(".gallery-photo img").count()>=1
      assert pg.locator(".gallery-photo img").first.evaluate("(e)=>e.complete && e.naturalWidth>0")
      assert "Glass Root Garden" in pg.locator("#detail").inner_text()
      assert "all rights reserved" in pg.locator("#detail").inner_text()
      assert pg.locator(".photo-review").count()>=1
      pg.screenshot(path=str(OUT/f"fabaceae-owner-authorized-private-{name}.png"),full_page=True)
      if summary["owner_permission_photo_instances"]==7:
         for sid in ("rhynchosia-minima","rhynchosia-senna","sesbania-drummondii"):
            pg.goto("http://127.0.0.1:8768/?species="+sid,wait_until="networkidle")
            imgs=pg.locator(".gallery-photo img")
            imgs.first.wait_for()
            assert all(imgs.nth(i).evaluate("(e)=>e.complete && e.naturalWidth>0") for i in range(imgs.count()))
            assert "Glass Root Garden" in pg.locator("#detail").inner_text()
            assert pg.locator(".photo-review").count()>=1
         pg.screenshot(path=str(OUT/f"fabaceae-owner-seven-source-photo-check-{name}.png"),full_page=True)
   pg.locator("button[data-mode='field']").click()
   assert pg.locator("button[data-mode='field']").get_attribute("aria-pressed")=="true"
   pg.locator("#search").fill("senegalia")
   assert pg.locator("#results button").count()>0
   assert not errors,errors
   print("FABACEAE_PHOTO_BROWSER_PASS",name,summary["verified_source_photos_displayed"],
     "photos",summary["species_with_verified_photos"],"species",flush=True)
   pg.close()
 browser.close()
