"""Step 6. Render ../header.png (1200 x 630 social card) with Playwright Chromium."""
import sys, os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from playwright.sync_api import sync_playwright

R = jload(os.path.join(DATA, "results.json"))
img = base64.b64encode(open(os.path.join(WORK, "header_map.png"), "rb").read()).decode()
FD = FONT_DIR
ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
    ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
    ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")])
n = R["survey"]["n"]
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:{BG};color:{FG};overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:64px;top:62px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};display:flex;gap:12px;align-items:center}}
.k b{{background:{COLOR['tea']};color:#fff;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:104px;margin:0;font:900 96px/.92 Fraunces,Georgia,serif;letter-spacing:-.02em;font-variation-settings:"SOFT" 60;width:680px}}
.d{{color:{COLOR['dinner']}}} .t{{color:{COLOR['tea']}}} .s{{color:{COLOR['supper']}}}
p{{position:absolute;left:64px;top:340px;width:560px;margin:0;font-size:25px;line-height:1.36}}
.f{{position:absolute;left:64px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:{MUTED}}}
.m{{position:absolute;left:650px;top:-8px;height:646px;z-index:0}} h1,p,.k,.f{{z-index:1}}
</style></head><body>
<div class="k"><b>Data study</b><span>Dialect × food</span></div>
<h1><span class="d">Dinner,</span> <span class="t">tea</span> or <span class="s">supper?</span></h1>
<p>{n:,} survey answers on what Britain calls its evening meal, and the line where tea gives way to dinner.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<img class="m" src="data:image/png;base64,{img}">
</body></html>"""
tmp = os.path.join(WORK, "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + tmp); pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
print("header.png written")
