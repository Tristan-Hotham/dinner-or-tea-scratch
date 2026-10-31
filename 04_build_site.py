"""Step 4. Build ../index.html from code/page_template.html: numbers from data/results.json (see fill.py),
page data from WORK/site.json embedded as `const D = ...`, and the shared full-screen map snippet."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

# the claims made in words on the page, checked against the data
assert R["band"]["North"]["share"]["tea"] > .7 and R["band"]["South"]["share"]["dinner"] > .7
assert abs(R["band"]["Midlands"]["share"]["tea"] - R["band"]["Midlands"]["share"]["dinner"]) < .03
assert all(R["region"][r]["share"]["tea"] > .7 for r in NORTH)
assert all(R["region"][r]["share"]["dinner"] > .5 for r in SOUTH)
assert R["region"]["South West"]["share"]["tea"] > R["region"]["South East"]["share"]["tea"]
cn = R["counties"]["by_name"]
for c in ("Somerset", "Gloucestershire"):
    assert cn[c]["share"]["tea"] > .4, c
assert [r["county"] for r in R["counties"]["uk_top_tea"][:2]] == ["East Riding of Yorkshire", "Lancashire"]
assert [r["county"] for r in R["counties"]["uk_top_dinner"][:2]] == ["Hertfordshire", "Greater London"]
assert sorted(cn, key=lambda c: cn[c]["share"]["tea"] if cn[c]["n"] >= 30 else 9)[:2] == ["Greater London", "Hertfordshire"]
assert R["nation"]["Wales"]["share"]["tea"] > .5 and R["nation"]["Scotland"]["share"]["dinner"] > .5 and R["nation"]["Northern Ireland"]["share"]["dinner"] > .7
assert R["places"]["Glasgow"]["dinner"] > .75 and R["places"]["Edinburgh"]["tea"] > .4
assert M["age_by_band"]["South"]["p"] < .001 and M["age_by_band"]["North"]["p"] > .05 and M["interaction"]["p"] < .001
assert M["age_by_band"]["Midlands"]["p"] < .05 and M["age_by_band"]["Scotland"]["p"] < .05
assert M["main"]["yr"]["or"] < 1 and R["gender"]["chi2_p_fm"] > .05
assert [r["region"] for r in R["supper"]["top_regions"][:3]] == ["South West", "South East", "London"]
assert set(r["region"] for r in R["supper"]["bottom_regions"]) >= {"North West", "North East"}
assert R["counties"]["uk_top_supper"][0]["county"] == "Aberdeenshire"
yd, yt = R["counties"]["yougov_dinner_ranks"], R["counties"]["yougov_tea_ranks"]
assert (yd["East Sussex"]["rank"], yd["Essex"]["rank"], yd["Kent"]["rank"]) == (4, 3, 7)
assert (yt["Greater Manchester"]["rank"], yt["Tyne and Wear"]["rank"], yt["Merseyside"]["rank"]) == (12, 3, 6)
w = R["england_check"]["weighted"]
assert all(abs(w[k] - R["yougov"]["england"][k]) < .05 for k in WORDS)
assert .3 < R["england_check"]["nw_sample"] < .35
assert R["year"]["std_dinner_max"] - R["year"]["std_dinner_min"] < .12

site = open(os.path.join(WORK, "site.json"), encoding="utf-8").read()
t = fill(open(os.path.join(HERE := os.path.dirname(os.path.abspath(__file__)), "page_template.html"), encoding="utf-8").read())
t = t.replace("/*DATA*/", "const D = " + site + ";")
t = t.replace("/*FULLSCREEN*/", open(os.path.join(HERE, "fullscreen_snippet.html"), encoding="utf-8").read())
check_visible(t.replace("const D = " + site, ""), "index.html")
assert "{{" not in t.replace("{{DOI}}", "").replace("https://blog.tristanhotham.com/2026/10/31/dinner-or-tea/", ""), re.findall(r"\{\{.*?\}\}", t)[:5]
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t.encode()) // 1024, "KB")
