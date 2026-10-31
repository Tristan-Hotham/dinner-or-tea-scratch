"""Step 8. Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo)."""
import sys, os, zipfile, json as _json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

REL = os.path.join(ROOT, "release"); NAME = "Hotham_Dinner_Tea_or_Supper"
# claims in words in the blog's alt text, checked
E = R["england_check"]
assert round(E["weighted"]["dinner"] * 100) == 55 and round(E["weighted"]["tea"] * 100) == 40 and round(E["raw"]["dinner"] * 100) == 44 and round(E["raw"]["tea"] * 100) == 53
assert round(R["region"]["London"]["share"]["dinner"] * 100) == 87 and round(R["region"]["Wales"]["share"]["tea"] * 100) == 57
assert R["age"]["by_band"]["South"][5]["supper"] > .19
post = fill(open(os.path.join(HERE := os.path.dirname(os.path.abspath(__file__)), "blog_template.html"), encoding="utf-8").read())
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
check_visible(post, "post")
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
meta = {"title": "Dinner, tea or supper? What Britain calls its evening meal",
        "slug": "dinner-or-tea",
        "excerpt": f"{R['survey']['n']:,} answers from the Our Dialects survey, mapped: tea in the north, dinner in the south, a tea line across the Midlands, and no sign of dinner moving north.",
        "seo_description": "Map of what Britain calls its evening meal: dinner, tea or supper, from 12,522 dialect survey answers, with the tea line and age trends.",
        "tags": ["dialect", "food", "dinner", "tea", "supper", "maps", "data visualisation", "Our Dialects", "British English"],
        "header_alt": f"Title card reading 'Dinner, tea or supper?' in blue, brown and purple on cream, beside a map of Great Britain and Northern Ireland shaded brown where the evening meal is tea, across northern England and Wales, and blue where it is dinner, across the south, Glasgow and Northern Ireland, with a black line between them. Text: {R['survey']['n']:,} survey answers on what Britain calls its evening meal."}
assert len(meta["seo_description"]) < 160 and f"{R['survey']['n']:,}" in meta["seo_description"]
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst): os.remove(dst)
    os.link(src, dst)


link(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/dinner-or-tea_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "map"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__": continue
            z.write(os.path.join(ROOT, d, fn), f"dinner-or-tea/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html", "header.png"):
        z.write(os.path.join(ROOT, fn), f"dinner-or-tea/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("``", "\u201c").replace("''", "\u201d").replace("$<$", "<").replace("\\&", "&")
zmeta = {"title": "Dinner, Tea or Supper? What Britain Calls Its Evening Meal: Mapping 12,522 Answers from the Our Dialects Survey",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: https://maps.tristanhotham.com/dinner-or-tea/. Data and code: https://github.com/Tristan-Hotham/dinner-or-tea. Survey answers \u00a9 the Our Dialects project (University of Manchester), used with credit; only aggregates are published.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["dialect", "British English", "dialect geography", "dinner", "tea", "supper", "meal names", "apparent time", "Our Dialects", "maps"],
         "license": "cc-by-4.0", "access_right": "open", "language": "eng",
         "related_identifiers": [{"identifier": "https://github.com/Tristan-Hotham/dinner-or-tea", "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": "https://maps.tristanhotham.com/dinner-or-tea/", "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.ourdialects.uk/maps/meal/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://doi.org/10.5281/zenodo.23691943", "relation": "references", "resource_type": "publication-workingpaper"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", re.sub(r"<!--.*?-->", "", post, flags=re.S)).split())
print("blog words", words, "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
