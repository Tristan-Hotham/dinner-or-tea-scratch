# Reddit post

## Title

[OC] Dinner, tea or supper? 75% of northern English answers call the evening meal tea, 74% of southern ones call it dinner: 12,522 dialect survey answers mapped, with the "tea line" between them

## Body

I smoothed 12,522 answers from the Our Dialects survey (University of Manchester, 2013 to 2024) to the question "what do you call your evening meal?" and drew the line where tea and dinner are level. It runs from the Severn estuary round Birmingham and east to the Wash. Wales is 57% tea; Scotland (61%) and Northern Ireland (79%) mostly dinner. Is dinner taking over? Younger southerners say it more (odds ratio 0.79 per decade of age), but in the north there is no age gap at all (0.97, p = 0.22), and no rise over twelve years. Supper is the word of over 65s in the south (20%). Caveat: a volunteer survey, young and very northern; reweighted to regional populations it matches YouGov's 2018 figures for England within a few points.

Interactive version (with a "what do they say near you?" search): https://maps.tristanhotham.com/dinner-or-tea/

## Source comment

Source: Our Dialects meal map (https://www.ourdialects.uk/maps/meal/, copyright the Our Dialects project, University of Manchester), 12,522 answers used with credit for aggregate analysis only, individual answers not republished. YouGov 2018, "Dinner time or tea time? It depends where you live" (published figures). ONS boundaries and Census 2021 regional populations (OGL v3.0, contains OS data © Crown copyright and database right 2026).

Tools: Python (pandas, NumPy, SciPy, geopandas, statsmodels, scikit-image, matplotlib). Smoothing: Gaussian kernel, 16 km where answers are dense (chosen by cross-validation), widened up to 32 km where sparse; areas with fewer than 10 weighted answers left blank. Age and year effects from logistic regressions with region.

Interactive version: https://maps.tristanhotham.com/dinner-or-tea/
Blog post: https://blog.tristanhotham.com/2026/10/31/dinner-or-tea/
Paper: https://doi.org/{{DOI}}
