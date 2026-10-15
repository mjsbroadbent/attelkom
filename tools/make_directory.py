"""Builds the MyPage@Attelkom member directory (users/index.html) and its status icons.

    python3 tools/make_directory.py

Real member sites are found by looking for users/<Name1234>/index.html; they are listed as
online. The made-up accounts in tools/accounts.json (dead, unpaid or "moving to new servers")
are listed as offline and link to nothing that exists. Add a site by creating its folder,
add a fake account by adding a line to accounts.json, then run this again.
"""
import html
import json
import os
import random
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS = os.path.join(ROOT, "users")
ACCOUNTS = os.path.join(ROOT, "tools", "accounts.json")

# Titles for the real sites where the page's own <title> is mangled or too long.
TITLE_FIX = {
    "Artyom4471": "VYSHKA 1999 :: Neftyanik Nurzhan :: East stand",
    "Erbol8645": "Irad's biggest webring",
}
UPDATED = {  # last-updated dates for the real sites, in the spirit of their content
    "Ahmet2321": "2001-03-11", "Aizada6121": "2003-06-02", "Artyom4471": "1999-11-28", "Asel3317": "2002-04-14",
    "Bolot7720": "2000-09-17", "Daniyar8645": "2004-01-09", "Emil6304": "1999-12-30", "Erbol8645": "2003-08-21",
    "Gary3498": "1997-08-02", "Gulzat2915": "2001-10-05", "Joldosh3145": "2004-07-19", "Kanykei5093": "2002-11-23",
    "Marat4086": "2000-05-30", "Maryam5461": "2003-02-27", "Ramiro8152": "2001-06-16", "Zarina4652": "2002-12-08",
}


# ------------------------------------------------------------------ icons

def pixel_font(size):
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    return f


def badge(text, led, fg, bg, frames):
    """A 62x15 beveled status badge with an LED, like a 1998 'server status' GIF."""
    out = []
    for lit in frames:
        im = Image.new("RGB", (62, 15), bg)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.line([(0, 14), (0, 0), (61, 0)], fill="#ffffff")
        d.line([(1, 14), (61, 14), (61, 1)], fill="#404040")
        col = led if lit else "#303030"
        d.ellipse((4, 3, 12, 11), fill=col, outline="#000000")
        if lit:
            d.point((6, 5), fill="#ffffff")
        d.text((16, 2), text, font=pixel_font(9), fill=fg)
        out.append(im.convert("P", palette=Image.ADAPTIVE, colors=16))
    return out


def make_icons():
    img = os.path.join(ROOT, "images")
    on = badge("ONLINE", "#00ff00", "#00ff00", "#000000", [True, False])
    on[0].save(os.path.join(img, "online.gif"), save_all=True, append_images=on[1:], duration=[700, 300], loop=0)
    off = badge("OFFLINE", "#ff0000", "#a0a0a0", "#202020", [True])
    off[0].save(os.path.join(img, "offline.gif"))
    # a little blinking NEW! tag for recently updated pages
    frames = []
    for c in ("#ff0000", "#ffff00"):
        im = Image.new("RGB", (28, 11), "#ffffff")
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.rectangle((0, 0, 27, 10), fill=c)
        d.text((2, 0), "NEW!", font=pixel_font(9), fill="#000080" if c == "#ffff00" else "#ffffff")
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=8))
    frames[0].save(os.path.join(img, "new_dir.gif"), save_all=True, append_images=frames[1:], duration=400, loop=0)


# ------------------------------------------------------------------ fake accounts

NAMES = {
    "turkic": "Aibek Nurlan Bakyt Kubat Almaz Ulan Talant Azamat Ermek Chyngyz Bekzhan Mirlan Askar Dastan Kanat Medet "
              "Nursultan Aigul Ainura Cholpon Gulnara Jyldyz Nazira Saltanat Begimai Aidana Meerim Elnura Burul Aisuluu "
              "Asylbek Kalys Temirlan Adilet Baktygul Nurzat Kairat Jengish Samat Tilek".split(),
    "iranic": "Farrukh Jamshid Rustam Sherzod Dilshod Bahrom Nodira Malika Shahlo Firuza Parviz Zafar Behruz Sanobar "
              "Ravshan Gulchehra Anvar Lola Sardor Kamola".split(),
    "slavic": "Sergei Dmitri Oleg Vladimir Natasha Olga Igor Pavel Yulia Svetlana Andrei Nikolai Tatiana Vadim Lena "
              "Kostya Galina Misha".split(),
    "korean": "Vitaly Sunhee Yongsu Eduard Marina Valeri Kimsu Larisa".split(),
    "other": "Mike Jennifer Brad Kevin Lupe Carlos Esteban Mariela Dwayne Heather Tomas Rosa".split(),
}
WEIGHTS = {"turkic": 5, "iranic": 3, "slavic": 3, "korean": 1, "other": 1}

TITLES = [
    "{n}'s Home Page", "Welcome to {n}'s World!!!", "{n} Online", "My Home Page - UNDER CONSTRUCTION",
    "Domashnyaya stranitsa {n}", "{n}din baraghy", "{n}'s Family Page", "{n}'s Horse Pictures",
    "Kara-Buura Ulak Fan Page", "Akyel Horses of the Talas Valley", "Chongtor Pony Club", "Nurzhan Neftchi Ultras '98",
    "TULPAR TALAS - Unofficial", "My Poems / Moi stikhi", "Class of 1999 - School No. 4 Talas", "TSU Physics Dept. Students",
    "Iradi Country-Folk Lyrics Archive", "Mor-Wave Underground", "Swift Hooves Fan Club", "Kymyz Recipes from My Grandmother",
    "Beshbarmak Central", "Cars of Nurzhan - Lada Tuning", "My Dog Bars", "Photos of Talas After the War",
    "Y2K Survival Guide", "Free MIDI Music!!!", "Jokes / Anekdoty", "Learn English with {n}",
    "St. Janyl Choir", "Komuz Tabs and Songs", "Eagle Hunters of the Chatkal", "Felt Shyrdak Patterns",
    "Talas Air Base Friends", "Chicago Iradi Community", "Iradi Stamps and Coins", "Fishing on Iyık-Köl",
    "Mountain Passes Weather Report", "{n}'s Guestbook", "Wedding Photos - Toy 2001", "Counter Strike Clan [TLS]",
    "Anime Fan Page", "Star Trek in Russian", "Hiking the Talas Alatau", "Bazaar Prices Weekly",
    "Shairlar / Poetry in Iradi", "Natasha's Cat Gallery", "Kara-Ak Derby History", "Free Webspace Tips",
    "Dial-Up Help for Beginners", "PC Repair Talas", "Soviet Badges Collection", "Matryoshka Shop",
    "Ulak Tartysh Rules Explained", "My Trip to Istanbul", "Korean Kimchi in Irad", "Iradi Rap",
    "Night Fishing Club", "Babushka's Garden", "Chess Club Nurzhan", "Bible Verses in Iradi",
    "Nooruz Celebration Photos", "Endurance Racing Results 2002", "Tractor Parts For Sale", "Taxi Drivers of Talas",
]


def make_accounts(n=118, seed=1999):
    rnd = random.Random(seed)
    taken = {d for d in os.listdir(USERS) if os.path.isdir(os.path.join(USERS, d))}
    groups = [g for g, w in WEIGHTS.items() for _ in range(w)]
    out = []
    while len(out) < n:
        name = rnd.choice(NAMES[rnd.choice(groups)])
        handle = f"{name}{rnd.randint(1000, 9999)}"
        if handle in taken:
            continue
        taken.add(handle)
        y = rnd.choices(range(1997, 2006), weights=[2, 4, 6, 7, 7, 6, 5, 3, 2])[0]
        date = f"{y}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}"
        out.append({
            "account": handle,
            "title": rnd.choice(TITLES).format(n=name),
            "updated": date,
            "kb": rnd.choice([12, 18, 24, 31, 47, 56, 88, 102, 164, 230, 512, 940, 1870, 4096, 9830]),
            "status": "offline",
        })
    return out


# ------------------------------------------------------------------ page

def real_sites():
    sites = []
    for d in sorted(os.listdir(USERS)):
        p = os.path.join(USERS, d, "index.html")
        if not re.fullmatch(r"[A-Z][A-Za-z]+\d{4}", d) or not os.path.exists(p):
            continue
        raw = open(p, "rb").read()
        m = re.search(rb"<title>(.*?)</title>", raw, re.I | re.S)
        title = TITLE_FIX.get(d) or (m.group(1).decode("utf-8", "replace").strip() if m else d)
        size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(os.path.join(USERS, d)) for f in fs)
        sites.append({"account": d, "title": html.unescape(title), "updated": UPDATED.get(d, "2001-01-01"),
                      "kb": max(1, size // 1024), "status": "online"})
    return sites


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


def page(rows):
    rows = sorted(rows, key=lambda r: r["account"].lower())
    letters = sorted({r["account"][0].upper() for r in rows})
    online = sum(r["status"] == "online" for r in rows)
    body = []
    current = None
    for i, r in enumerate(rows):
        L = r["account"][0].upper()
        if L != current:
            current = L
            body.append(f'<tr><td colspan="5" bgcolor="#003333"><a name="{L}"></a>'
                        f'<font face="Arial" size="2" color="#FFCC00"><b>&nbsp;{L}</b></font></td></tr>')
        bg = "#FFFFFF" if i % 2 else "#EEF5F0"
        on = r["status"] == "online"
        icon = '<img src="../images/online.gif" width="62" height="15" alt="ONLINE">' if on else \
               '<img src="../images/offline.gif" width="62" height="15" alt="OFFLINE">'
        new = ' <img src="../images/new_dir.gif" width="28" height="11" alt="NEW!">' if r["updated"] >= "2004-01-01" and on else ""
        acct = html.escape(r["account"])
        title = html.escape(r["title"])
        link = f'<a href="{acct}/">{acct}</a>' if on else f'<a href="{acct}/" class="dead">{acct}</a>'
        body.append(
            f'<tr bgcolor="{bg}"><td align="center">{icon}</td>'
            f'<td><font face="Courier New,Courier" size="2"><b>{link}</b></font></td>'
            f'<td><font face="Arial" size="2">{title}{new}</font></td>'
            f'<td align="center"><font face="Arial" size="1">{fmt_date(r["updated"])}</font></td>'
            f'<td align="right"><font face="Arial" size="1">{r["kb"]:,} KB</font></td></tr>')
    az = " | ".join(f'<a href="#{L}">{L}</a>' for L in letters)
    return f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
<META NAME="viewport" CONTENT="width=device-width, initial-scale=1.0">
<TITLE>MyPage@Attelkom - Member Directory</TITLE>
<link rel="icon" type="image/x-icon" href="../favicon.ico">
<STYLE TYPE="text/css">
<!--
body {{ font-family: Arial, Helvetica, sans-serif; }}
a {{ color: #006666; }}
a:hover {{ color: #FF0000; }}
a.dead {{ color: #808080; }}
.wrap {{ max-width: 760px; margin: 0 auto; }}
.scroll {{ overflow-x: auto; }}
-->
</STYLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" BACKGROUND="../images/horse_silhouettes_on_brown_background_seamless.jpg" TEXT="#000000">
<div class="wrap">
<div style="background:#FFFFFF">
<div style="background:#003333;text-align:center;padding:8px">
  <FONT FACE="Arial" SIZE="5" COLOR="#FFCC00"><B>MyPage@Attelkom</B></FONT><BR>
  <FONT FACE="Arial" SIZE="2" COLOR="#FFFFFF">Member Home Page Directory &middot; Katalog stranits &middot; Myuchölördün baraktary</FONT>
</div>
<div style="padding:8px">
<P><FONT SIZE="2">Every Attelkom dial-up account comes with <B>10 MB</B> of free web space at
<B>www.attelkom.com/users/<I>YourName1234</I>/</B>. Below are all member pages on our servers, sorted by account name.
Pages marked <IMG SRC="../images/offline.gif" WIDTH="62" HEIGHT="15" ALT="OFFLINE" ALIGN="absmiddle"> are temporarily unavailable
(account expired, unpaid or being moved to the new servers).</FONT></P>
<P ALIGN="center"><FONT SIZE="2"><B>{online}</B> pages online &middot; <B>{len(rows) - online}</B> offline &middot; {len(rows)} members</FONT></P>
<P ALIGN="center"><FONT FACE="Arial" SIZE="2"><B>{az}</B></FONT></P>
<div class="scroll">
<TABLE WIDTH="100%" BORDER="1" CELLPADDING="3" CELLSPACING="0" BORDERCOLOR="#99BBAA">
<TR BGCOLOR="#CCDDCC">
  <TH><FONT SIZE="2">Status</FONT></TH><TH><FONT SIZE="2">Account</FONT></TH><TH><FONT SIZE="2">Home page</FONT></TH>
  <TH><FONT SIZE="2">Updated</FONT></TH><TH><FONT SIZE="2">Size</FONT></TH>
</TR>
{chr(10).join(body)}
</TABLE>
</div>
<P><FONT SIZE="2">Want your page listed? Log in to the <A HREF="http://members.attelkom.net/ums/main.php?r=0">Customer Control Panel</A>
and tick <I>"List my page in the directory"</I>, or write to <A HREF="mailto:mypage@attelkom.net">mypage@attelkom.net</A>.</FONT></P>
<HR>
<P ALIGN="center"><FONT SIZE="1"><A HREF="../">Attelkom Online Home</A><BR>
&copy;1999-2004 Attelkom.net Irad Internet Services. Attelkom is not responsible for the content of member pages.</FONT></P>
<P ALIGN="center"><IMG SRC="../images/ie.gif" WIDTH="88" HEIGHT="31" ALT="Best viewed with Internet Explorer"></P>
</div>
</div>
</div>
</BODY>
</HTML>
"""


def main():
    make_icons()
    if not os.path.exists(ACCOUNTS):
        with open(ACCOUNTS, "w", encoding="utf-8") as f:   # one account per line, easy to edit by hand
            f.write("[\n" + ",\n".join(json.dumps(a, ensure_ascii=False) for a in make_accounts()) + "\n]\n")
    fake = json.load(open(ACCOUNTS))
    real = real_sites()
    realnames = {r["account"] for r in real}
    rows = real + [a for a in fake if a["account"] not in realnames]
    open(os.path.join(USERS, "index.html"), "w", encoding="utf-8").write(page(rows))
    print(f"{len(real)} online, {len(rows) - len(real)} offline")


if __name__ == "__main__":
    main()
