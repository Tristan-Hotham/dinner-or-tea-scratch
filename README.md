# Dinner, tea or supper?

What Britain calls its evening meal: 12,522 answers from the Our Dialects survey (2013 to 2024), smoothed into a map of dinner, tea and supper with the tea line where tea and dinner are level, models of age, survey year and gender, and a check against YouGov's 2018 figures. With a "what do they say near you?" search.

**Interactive version:** https://maps.tristanhotham.com/dinner-or-tea/

**Paper:** https://doi.org/{{DOI}}

**Blog post:** https://blog.tristanhotham.com/2026/10/31/dinner-or-tea/

This repository holds the interactive page, aggregate data and the analysis code for the data study *Dinner, tea or supper? What Britain calls its evening meal* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Companion study: [Barm, bap, cob or roll?](https://maps.tristanhotham.com/bread-rolls/)

## Headline results

- Tea in the north, dinner in the south: 75% of 5,817 answers from the north of England say tea; 74% of 3,669 from the south say dinner. The Midlands split 49% tea, 48% dinner. Overall: tea 51%, dinner 45%, supper 3.6%.
- The tea line runs from the Severn estuary round Birmingham and east past Derby and Nottingham to the Wash. Wales is 57% tea; Scotland 61% and Northern Ireland 79% dinner. Most tea: East Riding of Yorkshire (81%), Lancashire (80%); least: London (7%).
- Younger southerners say dinner more (odds ratio 0.79 per decade of age, p < 0.001; 79% at 18 to 24 against 57% at 50 to 64), but there is no age slope in the north (0.97, p = 0.22) and no rise in dinner across survey years (reweighted share 41% to 50%). Gender makes no difference.
- Supper is an older, southern word: 20% of southerners aged 65 and over, 6% at 18 to 24 (odds ratio 1.34 per decade, p < 0.001).
- Reweighted to regional populations, the survey gives England 55% dinner, 40% tea, 5% supper, against YouGov 2018's 57%, 36% and 5%.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (Leaflet map with layers panel, full-screen button and search, charts). Built by `code/04_build_site.py`. |
| `map/` | Smoothed overlays (`balance.png`, `lead.png`, `supper.png`), the smoothed grid for the search (`grid.json`) and place names for the search (`places.json`, OS Open Names and GeoNames). |
| `header.png` | Social card, 1200 x 630. |
| `data/meal_hexes.geojson` | Answers by word in 20 km hexagons, only hexagons with at least 10 answers (253 hexagons, 90% of answers). |
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

Answers were placed in counties and ONS regions and counted on a 2 km grid by word, then smoothed with a Gaussian kernel. Kernel width: 16 km, chosen by leave-one-cell-out prediction from 4 to 32 km, widened smoothly to 24 or 32 km where fewer than 10 weighted answers were nearby; cells still short are blank. The tea line is where the smoothed shares of tea and dinner are equal. Logistic regressions of dinner against tea on age, survey year, gender and region, overall and by area, with a likelihood ratio test of the age by area interaction; a separate model for supper. YouGov check: adult answers in each English region weighted to the region's share of England's population (Census 2021).

Caveats: a volunteer online survey, young (median age 22) and northern (33% of English answers from the North West); one question about the evening meal only, so the northern midday "dinner" is described from the literature, not measured; answers placed at postcode districts; few answers from Scotland, Wales and Northern Ireland.

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

Hotham, T. (2026). *Dinner, tea or supper? What Britain calls its evening meal*. Zenodo. https://doi.org/{{DOI}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
