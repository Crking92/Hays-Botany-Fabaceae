#!/usr/bin/env python3
"""Read-only test of exact individual iNaturalist photo source availability."""
import json,urllib.request,urllib.parse,time
ids=[349030024,640369868,4198176]
for pid in ids:
  for url in [
    f"https://api.inaturalist.org/v1/photos/{pid}",
    f"https://www.inaturalist.org/photos/{pid}.json",
    f"https://api.inaturalist.org/v1/observations?photo_id={pid}&per_page=10",
    f"https://www.inaturalist.org/photos/{pid}",
  ]:
    try:
      req=urllib.request.Request(url,headers={"User-Agent":"Hays-Botany-Photo-Probe/1.0","Accept":"application/json,text/html"})
      with urllib.request.urlopen(req,timeout=16) as resp:b=resp.read(350000)
      result={"pid":pid,"url":url,"bytes":len(b)}
      if b.lstrip().startswith(b"{") or b.lstrip().startswith(b"["):
        data=json.loads(b)
        result["total"]=data.get("total_results") if isinstance(data,dict) else None
        objs=data.get("results",[]) if isinstance(data,dict) else data if isinstance(data,list) else []
        result["rows"]=[{"observation":o.get("id"),"taxon":(o.get("taxon") or {}).get("name"),"photos":[{"id":p.get("id"),"license":p.get("license_code"),"attrib":p.get("attribution")} for p in (o.get("photos") or [])[:4]]} for o in objs[:3]]
      else:result["head"]=b[:45].decode("utf-8","replace")
      print("PHOTO_SOURCE_PROBE",json.dumps(result,ensure_ascii=False),flush=True)
    except Exception as ex:
      print("PHOTO_SOURCE_PROBE_FAIL",json.dumps({"pid":pid,"url":url,"error":str(ex)[:150]}),flush=True)
    time.sleep(.4)
