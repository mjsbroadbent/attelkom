#!/usr/bin/env python3
"""Pull 30 days of GoatCounter stats for every Irad site into noc/traffic.json (drawn by the NOC page).

Run by .github/workflows/traffic.yml every 4 hours. Needs GOATCOUNTER_TOKEN (a read-only API key for
irad.goatcounter.com, kept in the repo's secrets; never printed or written to a file). Only totals are saved:
views per page and per day, top referrers, browsers, systems, countries and screen sizes. Nothing about
individual visitors.

Paths are counted as host + path on every site (goatcounter.path = location.host + p), so the host is the
first path segment; pages on mjsbroadbent.github.io are split by their first folder. Visits to the NOC page
itself are left out.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://irad.goatcounter.com/api/v0"
OUT = Path(__file__).resolve().parent.parent / "noc" / "traffic.json"
DAYS = 30
SKIP = ("/noc/",)  # the console's own visits
HOST_ALIASES = {"wwv.attelkom.net": "www.attelkom.net"}
GH_PAGES = "mjsbroadbent.github.io"


def call(token, path, **params):
    q = urllib.parse.urlencode([(k, x) for k, v in params.items() for x in (v if isinstance(v, list) else [v])])
    req = urllib.request.Request(f"{API}{path}?{q}", headers={"Authorization": f"Bearer {token}",
                                                             "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                time.sleep(0.3)  # the API allows 4 requests a second
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 + attempt * 2)
                continue
            body = e.read().decode("utf-8", "replace")[:300]
            raise SystemExit(f"::error::GoatCounter {path}: HTTP {e.code} {body}")
    raise SystemExit(f"::error::GoatCounter {path}: rate limited")


def num(x):
    try:
        return int(str(x).replace(",", "").replace(" ", ""))
    except (TypeError, ValueError):
        return 0


def site_of(path):
    p = path.lstrip("/")
    host, _, rest = p.partition("/")
    host = HOST_ALIASES.get(host, host)
    if host == GH_PAGES:
        first = rest.split("/", 1)[0]
        return f"{host}/{first}" if first else host, "/" + rest.split("/", 1)[1] if "/" in rest else "/"
    return host or "(none)", "/" + rest


def main():
    token = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
    if not token:
        print("::warning::GOATCOUNTER_TOKEN is not set; traffic.json not updated")
        return
    end = dt.datetime.now(dt.timezone.utc).date()
    start = end - dt.timedelta(days=DAYS - 1)
    days = [(start + dt.timedelta(days=i)).isoformat() for i in range(DAYS)]
    rng = {"start": start.isoformat(), "end": end.isoformat()}

    # every page with its daily views (paged with exclude_paths)
    hits, seen = [], []
    while True:
        r = call(token, "/stats/hits", limit=100, daily="true", exclude_paths=seen, **rng)
        batch = [h for h in r.get("hits", []) if not h.get("event")]
        hits += batch
        seen += [str(h.get("path_id")) for h in r.get("hits", []) if h.get("path_id") is not None]
        if not r.get("more") or not r.get("hits") or len(hits) > 2000:
            break

    sites = {}
    for h in hits:
        path = h.get("path", "")
        if any(s in path for s in SKIP):
            continue
        site, page = site_of(path)
        daily = {d: 0 for d in days}
        for st in h.get("stats") or []:
            d = str(st.get("day", ""))[:10]
            if d in daily:
                daily[d] += num(st.get("daily"))
        views = num(h.get("count")) or sum(daily.values())
        s = sites.setdefault(site, {"views": 0, "daily": [0] * DAYS, "pages": {}})
        s["views"] += views
        s["daily"] = [a + b for a, b in zip(s["daily"], daily.values())]
        s["pages"][page] = s["pages"].get(page, 0) + views

    out_sites = {}
    for name, s in sorted(sites.items(), key=lambda kv: -kv[1]["views"]):
        top = sorted(s["pages"].items(), key=lambda kv: -kv[1])[:10]
        out_sites[name] = {"views": s["views"], "week": sum(s["daily"][-7:]), "daily": s["daily"],
                           "pages": len(s["pages"]), "top": [[p, c] for p, c in top]}

    def top(kind, n):
        r = call(token, f"/stats/{kind}", limit=n, **rng)
        rows = []
        for st in r.get("stats", []):
            name = st.get("name") or ("(direct)" if kind == "toprefs" else st.get("id")) or "(unknown)"
            rows.append([str(name), num(st.get("count"))])
        return rows

    daily_total = [sum(s["daily"][i] for s in out_sites.values()) for i in range(DAYS)]
    data = {
        "range": rng, "days": days,
        "total": sum(s["views"] for s in out_sites.values()), "week": sum(daily_total[-7:]),
        "daily": daily_total, "sites": out_sites,
        "refs": top("toprefs", 20), "browsers": top("browsers", 10), "systems": top("systems", 10),
        "locations": top("locations", 15), "sizes": top("sizes", 6),
    }

    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    old.pop("updated", None)
    if old == data:
        print("::notice::traffic unchanged")
        return
    data["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"::notice::traffic.json: {data['total']} views in {DAYS} days across {len(out_sites)} sites")


if __name__ == "__main__":
    sys.exit(main())
