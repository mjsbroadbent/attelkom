#!/usr/bin/env python3
"""Writes sitemap.xml and robots.txt for the old site. The pages themselves stay
untouched 1999 HTML; this only tells search engines what is there.

    python3 tools/make_sitemap.py

Left out: the 404 pages, frame navigation (nav/menu), the webring's
prev/next/rand redirect pages and anything carrying a noindex tag. The NOC page
is deliberately NOT named in robots.txt, which anyone can read; its own noindex
tag keeps it out of search."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "https://" + (ROOT / "CNAME").read_text().strip() + "/"
SKIP_NAMES = {"404.html", "not_found.html", "nav.html", "menu.html", "prev.html", "next.html", "rand.html"}

urls = []
for f in sorted(ROOT.rglob("*.html")):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith(".git") or f.name in SKIP_NAMES:
        continue
    if "noindex" in f.read_bytes().decode("latin-1").lower():
        continue
    urls.append(HOST + (rel[:-10] if rel.endswith("index.html") else rel))

(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {HOST}sitemap.xml\n")
print(len(urls), "pages in sitemap.xml")
