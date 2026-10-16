"""Put the MyPage@Attelkom free-hosting banner at the top of every member page.

    python3 tools/add_banners.py

Like GeoCities-era free hosts, Attelkom pays for MyPage by forcing a 468x60
Attelkom Jarnama banner onto members' pages. The block is inserted right after
<body> and is marked, so running the script again replaces it. Skipped: the
frameset pages (no body), nav/menu frames and the webring's redirect pages.
Each member gets the ad themes that suit the page (see THEMES).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"Erbol8645/next.html", "Erbol8645/prev.html", "Erbol8645/rand.html",
        "Emil6304/menu.html", "Gary3498/nav.html", "Marat4086/nav.html"}
THEMES = {"Daniyar8645": "dialup sketchy", "Joldosh3145": "dialup sketchy offnet", "Gary3498": "dialup diaspora",
          "Ahmet2321": "dialup diaspora local", "Ramiro8152": "dialup local", "Artyom4471": "dialup local"}
START, END = "<!-- MYPAGE-BANNER -->", "<!-- /MYPAGE-BANNER -->"


def block(member, depth):
    up = "../" * depth
    theme = THEMES.get(member, "dialup local")
    return (f'{START}\n<div style="clear:both;text-align:center;background:#ffffff;border-bottom:1px solid #999999;padding:3px 0 2px;margin:0 0 6px;font:10px Verdana,Arial,sans-serif;color:#000000;position:relative;z-index:99">'
            f'<div class="jarnama" data-size="468x60" data-theme="{theme}" style="display:inline-block"></div>'
            f'<div><a href="{up}index.html" target="_top" style="color:#0000cc">MyPage@Attelkom</a> - free home pages for every Attelkom subscriber! '
            f'&middot; <a href="{up}index.html" target="_top" style="color:#0000cc">member directory</a></div></div>\n'
            f'<script src="https://ads.attelkom.net/serve.js" data-theme="{theme}" defer></script>\n{END}\n')


def main():
    n = 0
    for p in sorted((ROOT / "users").glob("*/**/*.html")):
        rel = p.relative_to(ROOT / "users").as_posix()
        if rel in SKIP:
            continue
        s = p.read_bytes().decode("utf-8", errors="surrogateescape")
        if re.search(r"<frameset", s, re.I):
            continue
        s = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", s, flags=re.S)
        m = re.search(r"<body[^>]*>", s, re.I)
        if not m:
            print("no body:", rel)
            continue
        depth = len(Path(rel).parts) - 1
        s = s[:m.end()] + "\n" + block(rel.split("/")[0], depth) + s[m.end():]
        p.write_bytes(s.encode("utf-8", errors="surrogateescape"))
        n += 1
    print(n, "pages")


if __name__ == "__main__":
    main()
