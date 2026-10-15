# Notes for agents

- **Secret site index:** `noc/whitelist.html` lists every live Irad website (in-world: the Attelkom NOC's internal resource list). Whenever a new Irad site launches, moves to a new domain or subdomain, or is retired, update its row there (same style: number, linked host, one-line in-world description, status OK / OLD SERVER / FOREIGN HOST / PARTIAL / BLOCKED) and bump the "Last update" date. The page is reachable only through the hidden link on the © sign in `index.html`'s footer; don't link it from anywhere else.
- **Domain:** this old site is meant for www.attelkom.net (bare attelkom.net is the new site, repo attelkom-new). GitHub Pages can't serve the two from different repos, so for now it sits on wwv.attelkom.net (see `CNAME`); don't change `CNAME` without the owner.
- Links inside the site are relative; most front-page menu links are deliberately broken.
