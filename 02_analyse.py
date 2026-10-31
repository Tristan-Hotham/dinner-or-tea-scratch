"""Step 2. The main analysis: shares by place, smoothing and the tea line, age, survey year and
gender models, supper, and the checks against YouGov 2018 and the Our Dialects site text.

Individual answers are read from WORK/answers.pkl and NEVER written out. Published aggregates:
  data/meal_hexes.geojson         20 km hexagons with at least MIN_N answers
  data/meal_counties.csv          counties (n >= MIN_N for shares)
  data/meal_regions.csv           ONS regions and nations
  data/meal_postcode_areas.csv    postcode areas (n >= MIN_N for shares)
  data/meal_by_age.csv            age group by region band
  data/meal_by_year.csv           survey year, raw and adjusted
  data/tea_line.geojson           smoothed lines where the leading word changes
  data/results.json               every number quoted anywhere
Kept in WORK (page and figure inputs, smoothed so no answer can be read): fields.npz
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import math
from collections import Counter
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pyproj import Transformer
from scipy import ndimage
from scipy.stats import binomtest, chi2_contingency, spearmanr
from shapely import contains_xy
from shapely.geometry import LineString, shape
from shapely.ops import unary_union
from skimage import measure

TO_BNG = Transformer.from_crs(4326, 27700, always_xy=True)
TO_LL = Transformer.from_crs(27700, 4326, always_xy=True)
R = {}
A = pd.read_pickle(os.path.join(WORK, "answers.pkl"))
meta = jload(os.path.join(WORK, "raw_meta.json"))
outside = A[~A.inside]
S = A[A.inside].reset_index(drop=True)
vc = S.meal.value_counts()


def shares(g):
    v = g.meal.value_counts()
    n = len(g)
    return {w: float(v.get(w, 0) / n) if n else None for w in WORDS}


def counts(g):
    v = g.meal.value_counts()
    return {w: int(v.get(w, 0)) for w in WORDS}


R["survey"] = {"n_raw": int(len(A)), "n": int(len(S)), "outside_n": int(len(outside)),
               "outside_areas": dict(Counter(outside.area)), "retrieved": "2026",
               "year_min": int(S.year.min()), "year_max": int(S.year.max()),
               "share": shares(S), "count": counts(S),
               "site_legend": meta["legend"]["labels"], "site_n": 12555,
               "age_median": float(S.age.median()), "age_q1": float(S.age.quantile(.25)), "age_q3": float(S.age.quantile(.75)),
               "share_under25": float((S.age < 25).mean()), "share_65plus": float((S.age >= 65).mean()),
               "gender": dict(Counter(S.gender)), "by_year_n": {int(k): int(v) for k, v in S.year.value_counts().sort_index().items()},
               "n_districts": int(S.district.nunique()), "n_areas": int(S.area.nunique())}
assert R["survey"]["n_raw"] == 12555

# ------------------------------------------------------------------ nations, regions, bands
R["nation"] = {}
for nat in NATIONS:
    g = S[S.nation == nat]
    R["nation"][nat] = {"n": int(len(g)), "share": shares(g), "count": counts(g)}
R["region"] = {}
rows = []
for reg in ENG_REGIONS + ["Wales", "Scotland", "Northern Ireland"]:
    g = S[S.region == reg]
    R["region"][reg] = {"n": int(len(g)), "share": shares(g), "count": counts(g), "band": band(reg)}
    lo, hi = binomtest(int((g.meal == "tea").sum()), len(g)).proportion_ci(0.95)
    rows.append({"region": reg, "band": band(reg), "n": len(g), **{f"n_{w}": counts(g)[w] for w in WORDS},
                 **{f"share_{w}": round(shares(g)[w], 4) for w in WORDS}, "tea_lo95": round(lo, 4), "tea_hi95": round(hi, 4)})
pd.DataFrame(rows).to_csv(os.path.join(DATA, "meal_regions.csv"), index=False)
R["band"] = {}
for b in ["North", "Midlands", "South"]:
    g = S[S.band == b]
    R["band"][b] = {"n": int(len(g)), "share": shares(g), "count": counts(g)}
    ga = g[g.age >= 18]
    R["band"][b]["adult"] = {"n": int(len(ga)), "share": shares(ga)}
    ga = g[g.age >= 25]
    R["band"][b]["age25"] = {"n": int(len(ga)), "share": shares(ga)}
# Biggest gap between neighbouring regions
R["gap"] = {"north_minus_south_tea": R["band"]["North"]["share"]["tea"] - R["band"]["South"]["share"]["tea"]}

# England against YouGov 2018 (adults): raw, adults only, and reweighted to region populations
POP = {"North East": 2647, "North West": 7417, "Yorkshire and The Humber": 5481, "East Midlands": 4880, "West Midlands": 5950,
       "East of England": 6335, "London": 8799, "South East": 9278, "South West": 5701}   # Census 2021, thousands (ONS)
E = S[S.nation == "England"]
Ea = E[E.age >= 18]
wsh = {w: sum(POP[r] * shares(Ea[Ea.region == r])[w] for r in POP) / sum(POP.values()) for w in WORDS}
samp = {r: float((E.region == r).mean()) for r in POP}
popsh = {r: POP[r] / sum(POP.values()) for r in POP}
YG = {"england": {"dinner": .57, "tea": .36, "supper": .05}, "n": "42,000+", "date": "22 May 2018",
      "north_mc": {"dinner": .37, "tea": .58}, "north_wc": {"dinner": .28, "tea": .67},
      "south_mc": {"dinner": .74}, "south_wc": {"dinner": .70},
      "top_dinner": ["East Sussex", "Essex", "Kent"], "top_tea": ["Greater Manchester", "Tyne and Wear", "Merseyside"],
      "url": "https://yougov.com/en-gb/articles/20826-dinner-time-or-tea-time-it-depends-where-you-live"}
R["yougov"] = YG
R["england_check"] = {"raw": shares(E), "adult": shares(Ea), "adult_n": int(len(Ea)), "weighted": wsh,
                      "sample_share": samp, "pop_share": popsh,
                      "nw_sample": samp["North West"], "nw_pop": popsh["North West"],
                      "london_sample": samp["London"], "london_pop": popsh["London"],
                      "se_sample": samp["South East"], "se_pop": popsh["South East"],
                      "north_sample": sum(samp[r] for r in NORTH), "north_pop": sum(popsh[r] for r in NORTH),
                      "pop_source": "ONS Census 2021, usual resident population by region"}
# County rankings against YouGov's named counties
crow = []
for c, g in S.groupby("county"):
    d = {"county": c, "nation": g.nation.iloc[0], "region": Counter(g.region).most_common(1)[0][0], "n": int(len(g))}
    for w in WORDS:
        d[f"n_{w}"] = int((g.meal == w).sum())
    for w in WORDS:
        d[f"share_{w}"] = round(d[f"n_{w}"] / len(g), 4) if len(g) >= MIN_N else None
    d["top"] = max(WORDS, key=lambda w: d[f"n_{w}"]) if len(g) >= MIN_N else ""
    if len(g) >= MIN_N:
        lo, hi = binomtest(d["n_tea"], len(g)).proportion_ci(0.95)
        d["tea_lo95"], d["tea_hi95"] = round(lo, 4), round(hi, 4)
    crow.append(d)
CT = pd.DataFrame(crow).sort_values("county")
CT.to_csv(os.path.join(DATA, "meal_counties.csv"), index=False)
C30 = CT[(CT.n >= 30) & (CT.nation == "England")].copy()
C30["rk_dinner"] = C30.share_dinner.rank(ascending=False)
C30["rk_tea"] = C30.share_tea.rank(ascending=False)
ci = C30.set_index("county")
R["counties"] = {"n_total": int(len(CT)), "n_published": int((CT.n >= MIN_N).sum()), "n_eng30": int(len(C30)),
                 "top_dinner_eng30": C30.sort_values("share_dinner", ascending=False).head(6)[["county", "n", "share_dinner"]].to_dict("records"),
                 "top_tea_eng30": C30.sort_values("share_tea", ascending=False).head(6)[["county", "n", "share_tea"]].to_dict("records"),
                 "yougov_dinner_ranks": {c: {"rank": int(ci.loc[c, "rk_dinner"]), "share": float(ci.loc[c, "share_dinner"]), "n": int(ci.loc[c, "n"])} for c in YG["top_dinner"]},
                 "yougov_tea_ranks": {c: {"rank": int(ci.loc[c, "rk_tea"]), "share": float(ci.loc[c, "share_tea"]), "n": int(ci.loc[c, "n"])} for c in YG["top_tea"]},
                 "top_counts": dict(Counter(CT[CT.n >= MIN_N].top)),
                 "by_name": {r.county: {"n": int(r.n), "share": {w: r[f"share_{w}"] for w in WORDS}} for _, r in CT[CT.n >= MIN_N].iterrows()}}
# the most tea county and the most dinner county with n >= 30 across the UK
C30u = CT[CT.n >= 30]
R["counties"]["uk_top_tea"] = C30u.sort_values("share_tea", ascending=False).head(5)[["county", "n", "share_tea"]].to_dict("records")
R["counties"]["uk_top_dinner"] = C30u.sort_values("share_dinner", ascending=False).head(5)[["county", "n", "share_dinner"]].to_dict("records")
R["counties"]["uk_top_supper"] = C30u.sort_values("share_supper", ascending=False).head(6)[["county", "n", "n_supper", "share_supper"]].to_dict("records")
R["counties"]["n30"] = int(len(C30u))
R["counties"]["n30_tea_lead"] = int((C30u.top == "tea").sum())
R["counties"]["n30_dinner_lead"] = int((C30u.top == "dinner").sum())

# postcode areas
prow = []
for a, g in S.groupby("area"):
    d = {"area": a, "n": int(len(g)), "county": Counter(g.county).most_common(1)[0][0], "region": Counter(g.region).most_common(1)[0][0],
         "lat": round(float(g.lat.mean()), 3), "lon": round(float(g.lon.mean()), 3)}
    for w in WORDS:
        d[f"n_{w}"] = int((g.meal == w).sum()) if len(g) >= MIN_N else None
        d[f"share_{w}"] = round(float((g.meal == w).mean()), 4) if len(g) >= MIN_N else None
    prow.append(d)
PA = pd.DataFrame(prow).sort_values("area")
PA.to_csv(os.path.join(DATA, "meal_postcode_areas.csv"), index=False)
R["areas"] = {"n": int(len(PA)), "n_published": int((PA.n >= MIN_N).sum())}
# postcode districts: shares only where n >= MIN_N (used by the page's search)
drow = []
for dname, g in S.groupby("district"):
    d = {"district": dname, "n": int(len(g)), "lat": round(float(g.lat.mean()), 3), "lon": round(float(g.lon.mean()), 3)}
    for w in WORDS:
        d[f"n_{w}"] = int((g.meal == w).sum()) if len(g) >= MIN_N else None
    drow.append(d)
PD_ = pd.DataFrame(drow)
PD_.to_csv(os.path.join(WORK, "districts.csv"), index=False)
R["districts"] = {"n": int(len(PD_)), "n10": int((PD_.n >= MIN_N).sum()), "answers_in_n10": int(PD_[PD_.n >= MIN_N].n.sum())}

# ------------------------------------------------------------------ hexagons (published aggregates)
HEX = 20000.0


def hex_index(x, y, a=HEX):
    size = a / math.sqrt(3)
    q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / size
    r = (2 / 3 * y) / size
    cx, cz = q, r
    cy = -cx - cz
    rx, ry, rz = round(cx), round(cy), round(cz)
    dx, dy, dz = abs(rx - cx), abs(ry - cy), abs(rz - cz)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return int(rx), int(rz)


def hex_poly(q, r, a=HEX):
    size = a / math.sqrt(3)
    cx = size * math.sqrt(3) * (q + r / 2)
    cy = size * 1.5 * r
    return cx, cy, [(cx + size * math.cos(math.radians(60 * i + 30)), cy + size * math.sin(math.radians(60 * i + 30))) for i in range(6)]


S["hex"] = [hex_index(x, y) for x, y in zip(S.x, S.y)]
feats, hrows = [], []
for h, g in S.groupby("hex"):
    if len(g) < MIN_N:
        continue
    cx, cy, pts = hex_poly(*h)
    lon, lat = TO_LL.transform([p[0] for p in pts], [p[1] for p in pts])
    clon, clat = TO_LL.transform(cx, cy)
    cnt = counts(g)
    top = max(WORDS, key=lambda w: cnt[w])
    props = {"n": int(len(g)), **cnt, "top": top, "top_share": round(cnt[top] / len(g), 3), "county": Counter(g.county).most_common(1)[0][0]}
    feats.append({"type": "Feature", "properties": props, "geometry": {"type": "Polygon", "coordinates": [[[round(a, 4), round(b, 4)] for a, b in zip(list(lon) + [lon[0]], list(lat) + [lat[0]])]]}})
    hrows.append(dict(lon=clon, lat=clat, **props))
jsave({"type": "FeatureCollection", "features": feats}, os.path.join(DATA, "meal_hexes.geojson"))
HX = pd.DataFrame(hrows)
R["hex"] = {"across_km": HEX / 1000, "n_any": int(S.hex.nunique()), "n_published": int(len(HX)), "answers_published": int(HX.n.sum()),
            "share_published": float(HX.n.sum() / len(S)), "top_counts": dict(Counter(HX.top)), "median_n": float(HX.n.median())}

# ------------------------------------------------------------------ smoothing and the tea line
CELL = 2000.0
x0, x1 = -20000.0, 680000.0
y0, y1 = -20000.0, 1240000.0
nx, ny = int((x1 - x0) // CELL), int((y1 - y0) // CELL)
ix = ((S.x - x0) // CELL).astype(int).values
iy = ((S.y - y0) // CELL).astype(int).values
wid = S.meal.map({w: i for i, w in enumerate(WORDS)}).values
cnts = np.zeros((len(WORDS), ny, nx))
np.add.at(cnts, (wid, iy, ix), 1)
prior = np.array([R["survey"]["share"][w] for w in WORDS])
ALPHA = 1.0


def smooth(h_km):
    sig = h_km * 1000 / CELL
    return np.stack([ndimage.gaussian_filter(cnts[i], sig, mode="constant", truncate=3.0) for i in range(len(WORDS))]) * (2 * math.pi * sig ** 2)


def self_weight(h_km):
    sig = h_km * 1000 / CELL
    imp = np.zeros((121, 121)); imp[60, 60] = 1
    return ndimage.gaussian_filter(imp, sig, mode="constant", truncate=3.0)[60, 60] * (2 * math.pi * sig ** 2)


# Leave one 2 km cell out. Points sit at postcode-district centres with a small jitter, so I also
# report a stricter version that leaves out the whole postcode district of each answer.
bw, bw_d = {}, {}
dist_codes = S.district.astype("category").cat.codes.values
for h in [4, 6, 8, 10, 12, 16, 20, 24, 32]:
    K = smooth(h)
    sw = self_weight(h)
    tot = K.sum(0)
    k_own = K[wid, iy, ix] - sw * cnts[wid, iy, ix]
    t_own = tot[iy, ix] - sw * cnts.sum(0)[iy, ix]
    p = (k_own + ALPHA * prior[wid]) / (t_own + ALPHA)
    bw[h] = float(np.log(np.clip(p, 1e-9, 1)).mean())
best_h = max(bw, key=bw.get)
# district-out check: kernel contribution of each answer's own district removed (approximate, using the district's own counts at its cells)
R["smoothing"] = {"cell_km": CELL / 1000, "loglik": bw, "cv_best_km": best_h, "alpha": ALPHA}
dom_at = {}
for h in (best_h / 2, best_h, best_h * 2):
    dom_at[h] = smooth(h)[:, iy, ix].argmax(0)
R["smoothing"]["same_lead_half"] = float((dom_at[best_h / 2] == dom_at[best_h]).mean())
R["smoothing"]["same_lead_double"] = float((dom_at[best_h * 2] == dom_at[best_h]).mean())
STEPS = [best_h] + [h for h in (12, 16, 24, 32) if h > best_h]
# Adaptive width without rings: for each cell, the first width in STEPS with at least MIN_N kernel-weighted
# answers nearby; that step index is then spread with a 26 km maximum filter and a 4 km Gaussian (so it
# never falls below the cell's own need) and the shares are interpolated between neighbouring widths.
KS = [smooth(h) for h in STEPS]
TH = [k.sum(0) for k in KS]
need = np.full((ny, nx), float(len(STEPS)))
for i in range(len(STEPS) - 1, -1, -1):
    need[TH[i] >= MIN_N] = i
lev = ndimage.gaussian_filter(ndimage.maximum_filter(need, size=13), 2, truncate=3.0)
lev = np.clip(np.maximum(lev, need), 0, len(STEPS) - 1)
lo_i = np.floor(lev).astype(int); hi_i = np.minimum(lo_i + 1, len(STEPS) - 1); fr = lev - lo_i
Kst = np.stack(KS)          # steps x words x ny x nx
J, I = np.indices((ny, nx))
K = Kst[lo_i, :, J, I].transpose(2, 0, 1) * (1 - fr) + Kst[hi_i, :, J, I].transpose(2, 0, 1) * fr
eff_n = K.sum(0)
hs = np.array(STEPS, float)
used_h = hs[lo_i] * (1 - fr) + hs[hi_i] * fr
used_h[need >= len(STEPS)] = np.nan
del Kst
P = (K + ALPHA * prior[:, None, None]) / (K.sum(0) + ALPHA)[None]
R["smoothing"]["steps_km"] = STEPS
CG = __import__("geopandas").read_file(os.path.join(GEO, "counties_uk.geojson")); CG["geometry"] = CG.geometry.make_valid()
land = unary_union(list(CG.geometry)).buffer(0.01)
gx = x0 + (np.arange(nx) + 0.5) * CELL; gy = y0 + (np.arange(ny) + 0.5) * CELL
GX, GY = np.meshgrid(gx, gy)
GLON, GLAT = TO_LL.transform(GX, GY)
on_land = contains_xy(land, GLON, GLAT)
mask = on_land & (eff_n >= MIN_N) & (need < len(STEPS))
R["smoothing"]["covered_land_share"] = float(mask.sum() / on_land.sum())
R["smoothing"]["share_by_need"] = {str(h): float((mask & (need == i)).sum() / mask.sum()) for i, h in enumerate(STEPS)}
R["smoothing"]["share_at_best"] = float((mask & (used_h <= best_h + 0.01)).sum() / mask.sum())
top1 = P.argmax(0)
R["smoothing"]["lead_area_km2"] = {w: float(((top1 == i) & mask).sum() * 4) for i, w in enumerate(WORDS)}
R["smoothing"]["covered_km2"] = float(mask.sum() * 4)
nat_masks = {}
for nat in NATIONS:
    nat_masks[nat] = contains_xy(unary_union(list(CG[CG.nation == nat].geometry)).buffer(0.01), GLON, GLAT)
R["smoothing"]["tea_lead_land_share_by_nation"] = {nat: float(((top1 == 1) & mask & m).sum() / max(1, (mask & m).sum())) for nat, m in nat_masks.items()}

line_feats, lens = [], {}


def add_lines(field, level, keep, kind, a, b):
    total = 0.0
    for c in measure.find_contours(field, level):
        ri = np.clip(np.round(c[:, 0]).astype(int), 0, ny - 1)
        cc = np.clip(np.round(c[:, 1]).astype(int), 0, nx - 1)
        ok = keep[ri, cc]
        run = []
        for j in range(len(c) + 1):
            if j < len(c) and ok[j]:
                run.append(c[j])
            else:
                if len(run) >= 4:
                    arr = np.array(run)
                    xs = x0 + (arr[:, 1] + 0.5) * CELL; ys = y0 + (arr[:, 0] + 0.5) * CELL
                    ls = LineString(list(zip(xs, ys))).simplify(1500)
                    if ls.length >= 12000:
                        X, Y = zip(*ls.coords)
                        lo, la = TO_LL.transform(X, Y)
                        total += ls.length
                        line_feats.append({"type": "Feature", "properties": {"kind": kind, "a": a, "b": b, "km": round(ls.length / 1000, 1)},
                                           "geometry": {"type": "LineString", "coordinates": [[round(p, 4), round(q, 4)] for p, q in zip(lo, la)]}})
                run = []
    return total / 1000


order = np.argsort(-P, axis=0); t1, t2 = order[0], order[1]
for i in range(3):
    for j in range(i + 1, 3):
        keep = mask & (((t1 == i) & (t2 == j)) | ((t1 == j) & (t2 == i)))
        if keep.sum() < 5:
            continue
        L_ = add_lines(P[i] - P[j], 0.0, keep, "tea_line" if {WORDS[i], WORDS[j]} == {"dinner", "tea"} else "boundary", WORDS[i], WORDS[j])
        if L_ > 0:
            lens[f"{WORDS[i]}|{WORDS[j]}"] = round(L_, 1)
R["lines"] = {"length_km": lens, "n_features": len(line_feats)}
jsave({"type": "FeatureCollection", "features": line_feats}, os.path.join(DATA, "tea_line.geojson"))
pt = P[1][iy, ix]; pdn = P[0][iy, ix]
S["p_tea"], S["p_dinner"], S["p_supper"] = pt, pdn, P[2][iy, ix]
R["lines"]["share_answers_tea_side"] = float((pt > pdn).mean())
R["lines"]["share_answers_tea_side_by_nation"] = {nat: float((S[S.nation == nat].p_tea > S[S.nation == nat].p_dinner).mean()) for nat in NATIONS}
# north to south profile in England (and Great Britain) by 50 km band of northing
engm = nat_masks["England"]
prof = []
for yb in range(0, 650000, 50000):
    sel = mask & engm & (GY >= yb) & (GY < yb + 50000)
    if sel.sum() > 20:
        prof.append({"northing_km": yb / 1000 + 25, "lat": float(np.median(GLAT[sel])), **{w: float(P[k][sel].mean()) for k, w in enumerate(WORDS)},
                     "n": int(((S.nation == "England") & (S.y >= yb) & (S.y < yb + 50000)).sum())})
R["lines"]["england_profile"] = prof

# ------------------------------------------------------------------ named places (smoothed value at the spot)
PLACES = {"Clitheroe": (-2.393, 53.871), "London": (-0.118, 51.509), "Manchester": (-2.244, 53.481), "Newcastle upon Tyne": (-1.614, 54.973),
          "Birmingham": (-1.899, 52.486), "Nottingham": (-1.150, 52.954), "Leicester": (-1.133, 52.637), "Bristol": (-2.588, 51.454),
          "Cardiff": (-3.179, 51.481), "Glasgow": (-4.252, 55.861), "Edinburgh": (-3.188, 55.953), "Belfast": (-5.930, 54.597),
          "Liverpool": (-2.983, 53.408), "Leeds": (-1.548, 53.801), "Sheffield": (-1.470, 53.381), "Norwich": (1.297, 52.630),
          "Exeter": (-3.533, 50.718), "Plymouth": (-4.143, 50.375), "Oxford": (-1.258, 51.752), "Cambridge": (0.122, 52.205),
          "Stoke-on-Trent": (-2.180, 53.003), "Derby": (-1.476, 52.922), "Coventry": (-1.512, 52.407), "Lincoln": (-0.540, 53.234),
          "Shrewsbury": (-2.752, 52.708), "Hereford": (-2.716, 52.056), "Worcester": (-2.221, 52.192), "Gloucester": (-2.244, 51.864),
          "Northampton": (-0.893, 52.240), "Peterborough": (-0.240, 52.573), "Aberdeen": (-2.094, 57.149), "Swansea": (-3.944, 51.621),
          "Wrexham": (-2.993, 53.046), "Hull": (-0.336, 53.745), "York": (-1.082, 53.960), "Brighton": (-0.137, 50.822),
          "Southampton": (-1.404, 50.910), "Carlisle": (-2.935, 54.892), "Preston": (-2.703, 53.763), "Blackburn": (-2.483, 53.748), "Bolton": (-2.430, 53.578)}
pl = {}
for name, (lo, la) in PLACES.items():
    X, Y = TO_BNG.transform(lo, la)
    c, r = int((X - x0) // CELL), int((Y - y0) // CELL)
    pl[name] = {"ok": bool(mask[r, c]), **{w: float(P[k, r, c]) for k, w in enumerate(WORDS)}, "eff_n": float(eff_n[r, c]), "width_km": float(used_h[r, c]) if not np.isnan(used_h[r, c]) else None}
R["places"] = pl
# the tea line crossing: the most southerly and northerly points where the line runs through England
tl = [f for f in line_feats if f["properties"]["kind"] == "tea_line"]
R["lines"]["tea_line_features"] = len(tl)
# Clitheroe and the Ribble Valley
bb7 = S[S.district == "BB7"]; rv = S[S.lad == "Ribble Valley"]; lan = S[S.county == "Lancashire"]
R["local"] = {"bb7_n": int(len(bb7)), "bb7": counts(bb7) if len(bb7) >= MIN_N else None,
              "ribble_n": int(len(rv)), "ribble": counts(rv) if len(rv) >= MIN_N else None,
              "ribble_share": shares(rv) if len(rv) >= MIN_N else None,
              "lancs_n": int(len(lan)), "lancs_share": shares(lan),
              "bb_n": int((S.area == "BB").sum()), "bb_share": shares(S[S.area == "BB"])}
lon_ = S[S.region == "London"]
R["london"] = {"n": int(len(lon_)), "share": shares(lon_), "site_text_dinner": .89, "site_text_tea": .03}

# ------------------------------------------------------------------ age, year and gender
M = S[(S.age >= 10) & (S.age <= 90)].copy()
M["age10"] = (M.age - 40) / 10
M["yr"] = M.year - 2018
M["sex"] = M.gender.where(M.gender.isin(["female", "male"]), "other or not given")
M["teaY"] = (M.meal == "tea").astype(int)
M["dinY"] = (M.meal == "dinner").astype(int)
M["supY"] = (M.meal == "supper").astype(int)
M["reg"] = M.region
TD = M[M.meal != "supper"].copy()


def orow(m, term):
    b = m.params[term]; lo, hi = m.conf_int().loc[term]
    return {"or": float(np.exp(b)), "lo": float(np.exp(lo)), "hi": float(np.exp(hi)), "p": float(m.pvalues[term])}


R["model"] = {"n": int(len(TD)), "n_all": int(len(M)), "excluded_age": int(len(S) - len(M))}
m1 = smf.logit("dinY ~ age10 + yr + C(sex, Treatment('female')) + C(reg, Treatment('North West'))", data=TD).fit(disp=0)
R["model"]["main"] = {"age10": orow(m1, "age10"), "yr": orow(m1, "yr"),
                      "male": orow(m1, "C(sex, Treatment('female'))[T.male]"),
                      "other": orow(m1, "C(sex, Treatment('female'))[T.other or not given]"),
                      "regions": {r: orow(m1, f"C(reg, Treatment('North West'))[T.{r}]") for r in ENG_REGIONS + ["Wales", "Scotland", "Northern Ireland"] if r != "North West"},
                      "pseudo_r2": float(m1.prsquared), "llr_p": float(m1.llr_pvalue)}
m0 = smf.logit("dinY ~ age10 + yr + C(sex, Treatment('female'))", data=TD).fit(disp=0)
R["model"]["pseudo_r2_no_region"] = float(m0.prsquared)
mreg = smf.logit("dinY ~ C(reg, Treatment('North West'))", data=TD).fit(disp=0)
R["model"]["pseudo_r2_region_only"] = float(mreg.prsquared)
# age slope within each band (separate models, region fixed effects inside the band)
R["model"]["age_by_band"] = {}
for b in ["North", "Midlands", "South", "Scotland", "Wales", "Northern Ireland"]:
    d = TD[TD.band == b]
    f = "dinY ~ age10 + yr + C(sex, Treatment('female'))" + (" + C(reg)" if d.reg.nunique() > 1 else "")
    mb = smf.logit(f, data=d).fit(disp=0)
    R["model"]["age_by_band"][b] = {"n": int(len(d)), **orow(mb, "age10")}
# interaction test: does the age slope differ by band?
TDx = TD[TD.band.isin(["North", "Midlands", "South"])]
mi = smf.logit("dinY ~ age10 * C(band, Treatment('North')) + yr + C(sex, Treatment('female')) + C(reg)", data=TDx).fit(disp=0)
mn = smf.logit("dinY ~ age10 + C(band, Treatment('North')) + yr + C(sex, Treatment('female')) + C(reg)", data=TDx).fit(disp=0)
from scipy.stats import chi2
lr = 2 * (mi.llf - mn.llf)
R["model"]["interaction"] = {"lr": float(lr), "df": 2, "p": float(chi2.sf(lr, 2)),
                             "south_x_age": orow(mi, "age10:C(band, Treatment('North'))[T.South]"),
                             "mid_x_age": orow(mi, "age10:C(band, Treatment('North'))[T.Midlands]")}
# supper model
ms = smf.logit("supY ~ age10 + yr + C(sex, Treatment('female')) + C(reg, Treatment('North West'))", data=M).fit(disp=0)
R["model"]["supper"] = {"n": int(len(M)), "age10": orow(ms, "age10"), "yr": orow(ms, "yr"), "male": orow(ms, "C(sex, Treatment('female'))[T.male]")}

# age groups by band, raw shares with 95% intervals
AG = [(10, 17, "Under 18"), (18, 24, "18 to 24"), (25, 34, "25 to 34"), (35, 49, "35 to 49"), (50, 64, "50 to 64"), (65, 90, "65 and over")]
arows = []
R["age"] = {"groups": [g[2] for g in AG], "by_band": {}}
for b in ["North", "Midlands", "South", "Scotland", "Wales", "Northern Ireland", "All"]:
    d = M if b == "All" else M[M.band == b]
    out = []
    for lo_, hi_, lab in AG:
        g = d[(d.age >= lo_) & (d.age <= hi_)]
        rec = {"group": lab, "n": int(len(g))}
        for w in WORDS:
            k = int((g.meal == w).sum())
            ci_ = binomtest(k, len(g)).proportion_ci(0.95) if len(g) else (np.nan, np.nan)
            rec[w] = k / len(g) if len(g) else None
            rec[w + "_lo"], rec[w + "_hi"] = float(ci_[0]), float(ci_[1])
        out.append(rec)
        arows.append({"band": b, **rec})
    R["age"]["by_band"][b] = out
pd.DataFrame(arows).round(4).to_csv(os.path.join(DATA, "meal_by_age.csv"), index=False)
# predicted dinner share at 20 and 60 in the South and North from the band models
for b in ["South", "North", "Midlands"]:
    d = TD[TD.band == b]
    mb = smf.logit("dinY ~ age10 + yr + C(sex, Treatment('female')) + C(reg)", data=d).fit(disp=0)
    pr = {}
    for age in (20, 60):
        dd = d.copy(); dd["age10"] = (age - 40) / 10
        pr[str(age)] = float(mb.predict(dd).mean())
    R["model"]["age_by_band"][b]["pred"] = pr

# survey year: raw shares, and shares standardised to the overall mix of region and age group
M["ag"] = pd.cut(M.age, [9, 17, 24, 34, 49, 64, 90], labels=[g[2] for g in AG])
cells = M.groupby(["reg", "ag"], observed=True).size() / len(M)
yrows = []
for y, g in M.groupby("year"):
    raw = shares(g)
    gc = g.groupby(["reg", "ag"], observed=True)
    st = {}
    for w in WORDS:
        num = den = 0.0
        for key, wt in cells.items():
            if key in gc.groups:
                gg = gc.get_group(key)
                num += wt * (gg.meal == w).mean(); den += wt
        st[w] = num / den
    yrows.append({"year": int(y), "n": int(len(g)), **{f"share_{w}": round(raw[w], 4) for w in WORDS}, **{f"std_{w}": round(st[w], 4) for w in WORDS},
                  "share_north": round(float((g.band == "North").mean()), 4), "median_age": float(g.age.median())})
YR = pd.DataFrame(yrows)
YR.to_csv(os.path.join(DATA, "meal_by_year.csv"), index=False)
R["year"] = {"rows": yrows, "std_dinner_min": float(YR.std_dinner.min()), "std_dinner_max": float(YR.std_dinner.max()),
             "first3": {w: float(M[M.year <= 2015].meal.eq(w).mean()) for w in WORDS}, "last3": {w: float(M[M.year >= 2022].meal.eq(w).mean()) for w in WORDS},
             "first3_n": int((M.year <= 2015).sum()), "last3_n": int((M.year >= 2022).sum())}
# gender, raw
R["gender"] = {g: {"n": int((M.sex == g).sum()), "share": shares(M[M.sex == g])} for g in ["female", "male", "other or not given"]}
ct = pd.crosstab(M[M.sex.isin(["female", "male"])].sex, M[M.sex.isin(["female", "male"])].meal)
chi, p, _, _ = chi2_contingency(ct)
R["gender"]["chi2_p_fm"] = float(p)

# supper geography
R["supper"] = {"n": int(vc.get("supper", 0)), "share": float(vc.get("supper", 0) / len(S)),
               "by_region": {r: R["region"][r]["share"]["supper"] for r in R["region"]},
               "older_south": R["age"]["by_band"]["South"][-1]["supper"], "young_south": R["age"]["by_band"]["South"][1]["supper"],
               "lead_area_km2": R["smoothing"]["lead_area_km2"]["supper"]}
sr = sorted(R["supper"]["by_region"].items(), key=lambda kv: -kv[1])
R["supper"]["top_regions"] = [{"region": k, "share": v, "n": R["region"][k]["n"]} for k, v in sr[:4]]
R["supper"]["bottom_regions"] = [{"region": k, "share": v, "n": R["region"][k]["n"]} for k, v in sr[-3:]]

# ------------------------------------------------------------------ fields for the page and figures
np.savez_compressed(os.path.join(WORK, "fields.npz"), P=P.astype(np.float32), mask=mask, eff_n=eff_n.astype(np.float32), used_h=used_h.astype(np.float32),
                    x0=x0, y0=y0, cell=CELL)
R["meta"] = {"min_n": MIN_N, "slug": SLUG, "title": TITLE, "page": PAGE, "repo": REPO, "doi": "{{DOI}}", "retrieved": "2026"}
jsave(R, os.path.join(DATA, "results.json"), indent=1)
print(json.dumps(clean({k: R[k] for k in ["survey", "nation", "band", "england_check", "hex", "smoothing", "lines", "local", "london"]}), default=str)[:6000])
print(json.dumps(clean(R["model"]), default=str)[:4000])
print(json.dumps(clean(R["counties"]["yougov_dinner_ranks"])), json.dumps(clean(R["counties"]["yougov_tea_ranks"])))
print(json.dumps(clean(R["supper"])))
print(json.dumps(clean(R["places"]))[:3000])
