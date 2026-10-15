# Attelkom Online (old site)

The deprecated 1999-era Attelkom Online site of the Irad worldbuilding project, meant to live at **www.attelkom.com** (the current Attelkom site will be at attelkom.com). Most menu links on the front page are deliberately broken, as on a real abandoned ISP site.

- `users/` holds the MyPage@Attelkom member home pages, one folder per account in the `Name1234` format (`users/Erbol8645/` and so on).
- `users/index.html` is the member directory: the real pages are listed as online, and over a hundred made-up accounts as offline. It is built by `python3 tools/make_directory.py`, which also draws the status icons (`images/online.gif`, `images/offline.gif`, `images/new_dir.gif`). The made-up accounts are in `tools/accounts.json`, one per line. Add a member site by creating its folder and running the script again.
- `users/Erbol8645/urls.txt` is the "Irad's biggest webring" member list; each site's prev/next links use its position (`?id=`) in that list.
- Links inside the site are relative, so it works both at mjsbroadbent.github.io/attelkom/ and at the root of its own domain.
- `404.html` (GitHub Pages) and `not_found.html` (Neocities) are the same old-Apache "Not Found" page, pointing lost visitors to the directory.
- `tools/make_ephemera.py` draws the 1999 front-page extras: the 88×31 buttons in `images/badges/`, the visitor counter, the spinning globe, the guestbook mailbox and the header image. The top banner and one footer button are live Attelkom Jarnama ads (dial-up era).
- Search engine and Internet Explorer links go to the Wayback Machine's December 1999 copies; the site's own dead links are relative, so they land on the 404 page.
