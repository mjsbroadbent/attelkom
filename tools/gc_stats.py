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
import http.client
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://irad.goatcounter.com/api/v0"
OUT = Path(__file__).resolve().parent.parent / "noc" / "traffic.json"
DAYS = 30
SKIP = ("/noc/",)  # the console's own visits
HOST_ALIASES = {"wwv.attelkom.net": "www.attelkom.net"}
GH_PAGES = "mjsbroadbent.github.io"


class Transient(Exception):
    """GoatCounter was unreachable or answered with a server error; keep the old traffic.json."""


def call(token, path, tries=5, **params):
    q = urllib.parse.urlencode([(k, x) for k, v in params.items() for x in (v if isinstance(v, list) else [v])])
    req = urllib.request.Request(f"{API}{path}?{q}", headers={"Authorization": f"Bearer {token}",
                                                             "Content-Type": "application/json",
                                                             "User-Agent": "attelkom-noc-stats/1.1"})
    last = ""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
            time.sleep(0.3)  # the API allows 4 requests a second
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 or e.code >= 500:
                last = f"HTTP {e.code} {body}"
            else:
                raise SystemExit(f"GoatCounter {path}: HTTP {e.code} {body}")
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException,
                json.JSONDecodeError) as e:
            last = f"{type(e).__name__}: {e}"
        if attempt < tries - 1:
            time.sleep(3 + attempt * 5)
    raise Transient(f"GoatCounter {path}: {last}")


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
    call(token, "/me", tries=2)  # cheap check first: tells a dead API or key apart from a heavy query

    # every page with its daily views (paged with exclude_paths)
    # GoatCounter sometimes drops the connection on a big page of daily stats, so step the page size down
    hits, seen, limit = [], [], 50
    while True:
        try:
            r = call(token, "/stats/hits", tries=2, limit=limit, daily="true", exclude_paths=seen, **rng)
        except Transient:
            if limit <= 5:
                raise
            limit = max(5, limit // 3)
            print(f"::notice::GoatCounter dropped a page of hits; retrying {limit} at a time")
            continue
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
    # errors go to stdout as workflow annotations, so the reason shows on the run page without the log
    try:
        main()
    except Transient as e:
        print(f"::warning::{e}; traffic.json left as it was")
    except SystemExit as e:
        if e.code not in (None, 0):
            print(f"::error::{e.code}")
            sys.exit(1)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(f"::error::{type(e).__name__}: {str(e)[:300]}")
        sys.exit(1)
