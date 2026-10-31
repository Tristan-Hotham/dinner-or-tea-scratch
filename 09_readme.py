"""Step 9. README.md and LICENSE, numbers from data/results.json."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

kb = lambda f: f"{os.path.getsize(os.path.join(ROOT, f)) // 1024} KB"
t = """# Dinner, tea or supper?

What Britain calls its evening meal: {{survey.n|int}} answers from the Our Dialects survey ({{survey.year_min|raw}} to {{survey.year_max|raw}}), smoothed into a map of dinner, tea and supper with the tea line where tea and dinner are level, models of age, survey year and gender, and a check against YouGov's 2018 figures. With a "what do they say near you?" search.

**Interactive version:** https://maps.tristanhotham.com/dinner-or-tea/

**Paper:** https://doi.org/[[DOI]]

**Blog post:** [[BLOG_URL]]

This repository holds the interactive page, aggregate data and the analysis code for the data study *Dinner, tea or supper? What Britain calls its evening meal* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Companion study: [Barm, bap, cob or roll?](https://maps.tristanhotham.com/bread-rolls/)

## Headline results

- Tea in the north, dinner in the south: {{band.North.share.tea|pct0}} of {{band.North.n|int}} answers from the north of England say tea; {{band.South.share.dinner|pct0}} of {{band.South.n|int}} from the south say dinner. The Midlands split {{band.Midlands.share.tea|pct0}} tea, {{band.Midlands.share.dinner|pct0}} dinner. Overall: tea {{survey.share.tea|pct0}}, dinner {{survey.share.dinner|pct0}}, supper {{survey.share.supper|pct1}}.
- The tea line runs from the Severn estuary round Birmingham and east past Derby and Nottingham to the Wash. Wales is {{nation.Wales.share.tea|pct0}} tea; Scotland {{nation.Scotland.share.dinner|pct0}} and Northern Ireland {{nation.Northern Ireland.share.dinner|pct0}} dinner. Most tea: East Riding of Yorkshire ({{x_eryorks_tea}}), Lancashire ({{local.lancs_share.tea|pct0}}); least: London ({{london.share.tea|pct0}}).
- Younger southerners say dinner more (odds ratio {{model.age_by_band.South.or|f2}} per decade of age, {{x_p_south}}; {{x_south_dinner_young}} at 18 to 24 against {{x_south_dinner_older}} at 50 to 64), but there is no age slope in the north ({{model.age_by_band.North.or|f2}}, {{x_p_north}}) and no rise in dinner across survey years (reweighted share {{year.std_dinner_min|pct0}} to {{year.std_dinner_max|pct0}}). Gender makes no difference.
- Supper is an older, southern word: {{x_supper_old_south}} of southerners aged 65 and over, {{x_supper_young_south}} at 18 to 24 (odds ratio {{model.supper.age10.or|f2}} per decade, {{x_p_supage}}).
- Reweighted to regional populations, the survey gives England {{england_check.weighted.dinner|pct0}} dinner, {{england_check.weighted.tea|pct0}} tea, {{england_check.weighted.supper|pct0}} supper, against YouGov 2018's {{x_yg_dinner}}, {{x_yg_tea}} and {{x_yg_supper}}.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (Leaflet map with layers panel, full-screen button and search, charts). Built by `code/04_build_site.py`. |
| `map/` | Smoothed overlays (`balance.png`, `lead.png`, `supper.png`), the smoothed grid for the search (`grid.json`) and place names for the search (`places.json`, OS Open Names and GeoNames). |
| `header.png` | Social card, 1200 x 630. |
| `data/meal_hexes.geojson` | Answers by word in 20 km hexagons, only hexagons with at least 10 answers ({{hex.n_published|int}} hexagons, {{hex.share_published|pct0}} of answers). |
| `data/meal_counties.csv` | Answers and shares by county (shares only where n >= 10), with 95% intervals for tea. |
| `data/meal_regions.csv` | Answers and shares by ONS region and nation. |
| `data/meal_postcode_areas.csv` | Answers and shares by postcode area (shares only where n >= 10). |
| `data/meal_by_age.csv` | Shares by age group and area, with 95% intervals. |
| `data/meal_by_year.csv` | Shares by survey year, raw and reweighted to the overall mix of region and age. |
| `data/tea_line.geojson` | The smoothed tea line, and short lines where supper overtakes. |
| `data/counties.geojson`, `data/regions.geojson` | Simplified outlines (ONS). |
| `data/results.json` | Every number quoted on the page, in the paper, the blog post and the collage. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper (PDF and LaTeX), blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

Answers were placed in counties and ONS regions and counted on a 2 km grid by word, then smoothed with a Gaussian kernel. Kernel width: {{smoothing.cv_best_km|int}} km, chosen by leave-one-cell-out prediction from 4 to 32 km, widened smoothly to 24 or 32 km where fewer than 10 weighted answers were nearby; cells still short are blank. The tea line is where the smoothed shares of tea and dinner are equal. Logistic regressions of dinner against tea on age, survey year, gender and region, overall and by area, with a likelihood ratio test of the age by area interaction; a separate model for supper. YouGov check: adult answers in each English region weighted to the region's share of England's population (Census 2021).

Caveats: a volunteer online survey, young (median age {{survey.age_median|int}}) and northern ({{england_check.nw_sample|pct0}} of English answers from the North West); one question about the evening meal only, so the northern midday "dinner" is described from the literature, not measured; answers placed at postcode districts; few answers from Scotland, Wales and Northern Ireland.

## Sources and licences

- Survey answers: [Our Dialects](https://www.ourdialects.uk/maps/meal/) meal map, © the Our Dialects project (University of Manchester). Read from the project's public web map in 2026 and used for aggregate analysis with credit. **The individual answers are not included in this repository** and are not openly licensed; only aggregates with at least 10 answers and smoothed maps are published. Please use the project's own map for the answers.
- YouGov (2018), [Dinner time or tea time? It depends where you live](https://yougov.com/en-gb/articles/20826-dinner-time-or-tea-time-it-depends-where-you-live) (published figures quoted).
- Oxford English Dictionary (2013), "tea, n." (quoted). MacKenzie, Bailey and Turton, [Towards an updated dialect atlas of British English](https://eprints.lancs.ac.uk/id/eprint/168083/).
- Boundaries and Census 2021 regional populations: Office for National Statistics, Open Government Licence v3.0. Contains OS data © Crown copyright and database right 2026.
- Place names for the search: OS Open Names (OGL v3.0) and GeoNames (CC BY 4.0), as prepared for [dark-skies](https://github.com/Tristan-Hotham/dark-skies) (`data/uk_towns.csv`).
- Base map and hill shading tiles on the page © Esri. Map library: Leaflet.

My derived aggregates, map images and text are released under CC BY 4.0, with the credits above. Code is MIT (see `LICENSE`).

## Rerun

Needs Python 3 with numpy, pandas, scipy, geopandas, shapely, pyproj, scikit-image, statsmodels, matplotlib and Pillow, Playwright (header), xelatex and pdftotext (paper). Input paths are set in `code/common.py`: the survey file (`ourdialects_meal.json`, read from the project's web map; not redistributed) and ONS boundaries. Individual answers are kept outside the repository (`MEALWORK`).

```
python3 code/01_prepare.py      # place answers in counties and regions
python3 code/02_analyse.py      # shares, smoothing, tea line, models, results.json
python3 code/03_site_assets.py  # overlays, search grid, page data
python3 code/04_build_site.py   # index.html
python3 code/05_figures.py      # paper and blog figures
python3 code/06_header.py       # header.png
python3 code/07_paper.py        # paper PDF
python3 code/09_readme.py       # README and LICENSE
python3 code/08_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
```

## Citation

Hotham, T. (2026). *Dinner, tea or supper? What Britain calls its evening meal*. Zenodo. https://doi.org/[[DOI]]

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

""" + AI + "\n"
md = fill(t)
for bad in ("—", "–", "DSIT", "DCMS"):
    assert bad not in md, bad
assert "--" not in md.replace("|---|---|", "")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(md)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, the paper and the blog post, the figures and map images,
and the derived aggregate data in data/ and map/ are released under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/).

The survey answers behind the aggregates are (c) the Our Dialects project
(University of Manchester, https://www.ourdialects.uk/) and are not openly
licensed: they are not included here, and only aggregates of at least 10
answers are published, with credit. Boundaries and Census figures: Office for
National Statistics, Open Government Licence v3.0, contains OS data (c) Crown
copyright and database right 2026. Place names in map/places.json: OS Open
Names (OGL v3.0) and GeoNames (CC BY 4.0).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(md.split()), "words")
