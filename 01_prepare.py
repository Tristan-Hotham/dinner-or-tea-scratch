"""Step 1. Read the Our Dialects meal answers, place each in a nation, ONS region, county and local
authority, and write the individual answers to WORK (outside the repository). Also writes simplified
county and region outlines to data/ for the page and figures.

Output: WORK/answers.pkl (not published), data/counties.geojson, data/regions.geojson
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import geopandas as gpd
import pandas as pd
from pyproj import Transformer

raw = jload(RAW_SURVEY)
S = pd.DataFrame(raw["rows"])
S["lat"] = S.lat.astype(float); S["lon"] = S.lon.astype(float)
S["year"] = S.Year.astype(int); S["age"] = pd.to_numeric(S.Age, errors="coerce")
S["gender"] = S.Gender.replace({"NA": "not given"})
S["meal"] = S.Meal
S["district"] = S.Postcode.str.upper().str.strip()
S["area"] = S.district.str.extract(r"^([A-Z]{1,2})")[0]
assert set(S.meal) == set(WORDS), set(S.meal)
TO = Transformer.from_crs(4326, 27700, always_xy=True)
S["x"], S["y"] = TO.transform(S.lon.values, S.lat.values)
pts = gpd.GeoDataFrame(S, geometry=gpd.points_from_xy(S.lon, S.lat), crs=4326)

C = gpd.read_file(os.path.join(GEO, "counties_uk.geojson")).set_crs(4326, allow_override=True)
G = gpd.read_file(os.path.join(GEO, "uk_topo.json"), layer="rgn").set_crs(4326, allow_override=True)[["areanm", "geometry"]].rename(columns={"areanm": "region"})
LAD = gpd.read_file(os.path.join(GEO, "lad23_bsc.geojson")).to_crs(4326)[["LAD23NM", "geometry"]].rename(columns={"LAD23NM": "lad"})


def place(pts, poly, col):
    j = gpd.sjoin(pts[["geometry"]], poly, how="left", predicate="within")
    j = j[~j.index.duplicated()]
    out = j[col].copy()
    miss = out.isna()
    if miss.any():   # coastal points just outside a simplified outline: nearest polygon within ~3 km
        pm = pts.loc[miss, ["geometry"]].to_crs(27700)
        nn = gpd.sjoin_nearest(pm, poly.to_crs(27700), how="left", max_distance=3000)
        nn = nn[~nn.index.duplicated()]
        out.loc[miss] = nn[col]
    return out


S["county"] = place(pts, C[["county", "geometry"]], "county")
nation_of = dict(zip(C.county, C.nation))
S["nation"] = S.county.map(nation_of)
S["region"] = place(pts, G, "region")
S["lad"] = place(pts, LAD, "lad")
# the region of a point must agree with its nation
eng = S.nation == "England"
S.loc[~eng & S.nation.notna(), "region"] = S.loc[~eng & S.nation.notna(), "nation"]
bad = eng & ~S.region.isin(ENG_REGIONS)
S.loc[bad, "region"] = None
S["band"] = S.region.map(lambda r: band(r) if isinstance(r, str) else None)
S["inside"] = S.county.notna() & S.region.notna()
print("rows", len(S), "inside", int(S.inside.sum()), "outside", int((~S.inside).sum()))
print(S[~S.inside][["lat", "lon", "district"]].head(10))
S.drop(columns=["geometry"], errors="ignore").to_pickle(os.path.join(WORK, "answers.pkl"))
jsave({"source": raw["source"], "retrieved": raw["retrieved"], "legend": raw["legend"]}, os.path.join(WORK, "raw_meta.json"))

# simplified outlines for the page and figures (ONS, OGL v3)
Cs = C.to_crs(27700); Cs["geometry"] = Cs.simplify(250).buffer(0); Cs = Cs.to_crs(4326)
Cs["geometry"] = Cs.geometry.set_precision(1e-4)
Cs[["county", "nation", "geometry"]].to_file(os.path.join(DATA, "counties.geojson"), driver="GeoJSON", COORDINATE_PRECISION=4)
Gs = G.to_crs(27700); Gs["geometry"] = Gs.simplify(400).buffer(0); Gs = Gs.to_crs(4326)
Gs[["region", "geometry"]].to_file(os.path.join(DATA, "regions.geojson"), driver="GeoJSON", COORDINATE_PRECISION=4)
print("counties.geojson", os.path.getsize(os.path.join(DATA, "counties.geojson")) // 1024, "KB; regions", os.path.getsize(os.path.join(DATA, "regions.geojson")) // 1024, "KB")
