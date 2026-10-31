"""Step 3. Map overlays and compact page data.

  map/balance.png    tea against dinner: blue where dinner leads, brown where tea leads (Web Mercator overlay)
  map/lead.png       leading word, paler where the lead is narrow
  map/supper.png     share saying supper (transparent to full colour at 20% or more)
  map/grid.json      smoothed shares on a 0.05 x 0.03 degree grid, for the "near you" search (loaded on demand)
  map/places.json    villages, towns and cities for the search (OS Open Names, GB; GeoNames, NI), loaded on demand
  WORK/site.json     compact data embedded in index.html

All overlays and the grid are drawn from the smoothed field only where at least MIN_N kernel-weighted
answers are nearby, so no single answer can be read from them.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import base64
import geopandas as gpd
import pandas as pd
from PIL import Image
from pyproj import Transformer

TOWNS = "/home/claude/ref/dark-skies/data/uk_towns.csv"   # OS Open Names (GB) and GeoNames (NI), from github.com/Tristan-Hotham/dark-skies
os.makedirs(os.path.join(ROOT, "map"), exist_ok=True)
F = np.load(os.path.join(WORK, "fields.npz"))
P, mask, eff = F["P"], F["mask"], F["eff_n"]
x0, y0, cell = float(F["x0"]), float(F["y0"]), float(F["cell"])
ny, nx = mask.shape
R = jload(os.path.join(DATA, "results.json"))
TO = Transformer.from_crs(4326, 27700, always_xy=True)
LON0, LON1, LAT0, LAT1 = -8.4, 2.0, 49.8, 60.95


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


Wd = 1000
Hd = int(round(Wd * (merc_y(LAT1) - merc_y(LAT0)) / math.radians(LON1 - LON0)))
lons = LON0 + (np.arange(Wd) + 0.5) / Wd * (LON1 - LON0)
my = merc_y(LAT1) - (np.arange(Hd) + 0.5) / Hd * (merc_y(LAT1) - merc_y(LAT0))
lats = np.degrees(2 * np.arctan(np.exp(my)) - math.pi / 2)
LO, LA = np.meshgrid(lons, lats)


def sample(LO, LA):
    X, Y = TO.transform(LO, LA)
    ci = np.floor((X - x0) / cell).astype(int); ri = np.floor((Y - y0) / cell).astype(int)
    ok = (ci >= 0) & (ci < nx) & (ri >= 0) & (ri < ny)
    ci, ri = np.clip(ci, 0, nx - 1), np.clip(ri, 0, ny - 1)
    return ok & mask[ri, ci], ri, ci


m, ri, ci = sample(LO, LA)


def hx(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def ramp_balance(t):
    """t = tea share of (tea + dinner): 0 dinner blue, .5 neutral, 1 tea brown."""
    a, mid, b = hx(COLOR["dinner"]), hx(MID), hx(COLOR["tea"])
    t = np.clip(t, 0, 1)[..., None]
    lo = mid + (a - mid) * np.clip((0.5 - t) / 0.35, 0, 1)
    hi = mid + (b - mid) * np.clip((t - 0.5) / 0.35, 0, 1)
    return np.where(t < 0.5, lo, hi)


pd_, pt_, ps_ = P[0][ri, ci], P[1][ri, ci], P[2][ri, ci]
img = np.zeros((Hd, Wd, 4), dtype=np.uint8)
t = pt_ / np.maximum(pt_ + pd_, 1e-6)
img[..., :3] = ramp_balance(t).astype(np.uint8)
img[..., 3] = np.where(m, 235, 0)
Image.fromarray(img).save(os.path.join(ROOT, "map", "balance.png"), optimize=True)
img = np.zeros((Hd, Wd, 4), dtype=np.uint8)
top = np.argmax(np.stack([pd_, pt_, ps_]), 0)
ts = np.max(np.stack([pd_, pt_, ps_]), 0)
for k, w in enumerate(WORDS):
    sel = m & (top == k)
    img[sel, :3] = hx(COLOR[w])
    img[sel, 3] = (255 * (0.45 + 0.55 * np.clip((ts[sel] - 0.45) / 0.35, 0, 1))).astype(np.uint8)
Image.fromarray(img).save(os.path.join(ROOT, "map", "lead.png"), optimize=True)
img = np.zeros((Hd, Wd, 4), dtype=np.uint8)
img[m, :3] = hx(COLOR["supper"])
img[m, 3] = (255 * np.clip(ps_[m] / 0.2, 0, 1) ** 0.8).astype(np.uint8)
Image.fromarray(img).save(os.path.join(ROOT, "map", "supper.png"), optimize=True)

# search grid in plain latitude and longitude
GL0, GL1, GA0, GA1, DLO, DLA = -8.4, 2.0, 49.8, 60.95, 0.05, 0.03
gl = GL0 + (np.arange(int(round((GL1 - GL0) / DLO))) + 0.5) * DLO
ga = GA0 + (np.arange(int(round((GA1 - GA0) / DLA))) + 0.5) * DLA
GLO, GLA = np.meshgrid(gl, ga)
gm, gr, gc = sample(GLO, GLA)
code = lambda v: np.where(gm, np.clip(np.round(v * 100), 0, 100), 255).astype(np.uint8)
grid = {"lon0": GL0, "lat0": GA0, "dlon": DLO, "dlat": DLA, "nx": len(gl), "ny": len(ga),
        "dinner": base64.b64encode(code(P[0][gr, gc]).tobytes()).decode(),
        "tea": base64.b64encode(code(P[1][gr, gc]).tobytes()).decode(),
        "n": base64.b64encode(np.where(gm, np.clip(np.round(eff[gr, gc]), 0, 254), 255).astype(np.uint8).tobytes()).decode(),
        "note": "Smoothed shares (per cent) of dinner and tea; supper = 100 - dinner - tea. n = kernel-weighted answers nearby, capped at 254. 255 = no data."}
jsave(grid, os.path.join(ROOT, "map", "grid.json"))

# places: OS Open Names (GB) and GeoNames (NI)
T = pd.read_csv(TOWNS)
T = T[T.kind.isin(["City", "Town", "Village"])].copy()
T["k"] = T.kind.map({"City": 3, "Town": 2, "Village": 1})
T = T.sort_values(["k", "name"], ascending=[False, True])
places = [[r["name"], round(r.lat, 4), round(r.lon, 4), int(r.k), r.county] for _, r in T.iterrows()]
jsave(places, os.path.join(ROOT, "map", "places.json"))
towns = [p for p in places if p[3] >= 2]

# boundaries for the page (lighter than data/)
C = gpd.read_file(os.path.join(DATA, "counties.geojson")).to_crs(27700)
C["geometry"] = C.simplify(700).buffer(0)
C = C.to_crs(4326)
cfeat = []
for _, r in C.iterrows():
    g = r.geometry
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    rings = [[[round(y, 3), round(x, 3)] for x, y in p.exterior.coords] for p in polys if p.area > 1e-4]
    cfeat.append([r.county, r.nation, rings])
CT = pd.read_csv(os.path.join(DATA, "meal_counties.csv"))
ctab = {r.county: [int(r.n), None if pd.isna(r.share_dinner) else r.share_dinner, None if pd.isna(r.share_tea) else r.share_tea,
                   None if pd.isna(r.share_supper) else r.share_supper, r.region] for _, r in CT.iterrows()}
H = jload(os.path.join(DATA, "meal_hexes.geojson"))
hexes = [[[[round(a[1], 3), round(a[0], 3)] for a in f["geometry"]["coordinates"][0][:-1]], f["properties"]["n"], f["properties"]["dinner"],
          f["properties"]["tea"], f["properties"]["supper"], f["properties"]["county"]] for f in H["features"]]
Lines = jload(os.path.join(DATA, "tea_line.geojson"))
lines = [[f["properties"]["kind"], f["properties"]["a"], f["properties"]["b"], [[c[1], c[0]] for c in f["geometry"]["coordinates"]]] for f in Lines["features"]]
Dd = pd.read_csv(os.path.join(WORK, "districts.csv"))
districts = [[r.district, r.lat, r.lon] + ([int(r.n), int(r.n_dinner), int(r.n_tea), int(r.n_supper)] if r.n >= MIN_N else []) for _, r in Dd.iterrows()]
PA = pd.read_csv(os.path.join(DATA, "meal_postcode_areas.csv"))
areas = [[r.area, r.lat, r.lon, int(r.n)] + ([r.share_dinner, r.share_tea, r.share_supper] if r.n >= MIN_N else []) + [r.county] for _, r in PA.iterrows()]
site = {"R": R, "hexes": hexes, "lines": lines, "counties": cfeat, "ctab": ctab, "towns": towns, "districts": districts, "areas": areas,
        "bounds": [[LAT0, LON0], [LAT1, LON1]]}
jsave(site, os.path.join(WORK, "site.json"))
for f in ("balance.png", "lead.png", "supper.png", "grid.json", "places.json"):
    print(f, os.path.getsize(os.path.join(ROOT, "map", f)) // 1024, "KB")
print("site.json", os.path.getsize(os.path.join(WORK, "site.json")) // 1024, "KB", Wd, Hd, "towns", len(towns), "places", len(places))
