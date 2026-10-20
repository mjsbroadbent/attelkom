import os, urllib.request, urllib.parse, json, time
T=os.environ["GOATCOUNTER_TOKEN"].strip()
B="https://irad.goatcounter.com/api/v0"
def go(p):
    req=urllib.request.Request(B+p,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: b=r.read().decode()[:160]; print(f"::notice::{r.status} {p} -> {b}")
    except urllib.error.HTTPError as e: print(f"::notice::{e.code} {p} -> {e.read().decode()[:160]}")
    time.sleep(0.4)
for p in ["/me","/stats/total","/stats/total?start=2026-09-21&end=2026-10-20","/stats/hits","/stats/hits?limit=5","/stats/hits?limit=5&start=2026-09-21&end=2026-10-20","/stats/hits?limit=5&start=2026-09-21T00:00:00Z&end=2026-10-20T23:59:59Z","/stats/hits?limit=5&daily=true","/stats/toprefs?limit=3","/stats/browsers?limit=3"]:
    go(p)
