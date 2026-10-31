"""Shared paths, constants and palette for the dinner-or-tea study.

Raw inputs (read in place, never copied into the repository):
  RAW_SURVEY  Our Dialects "meal" map answers, read from the project's public web map
              (https://www.ourdialects.uk/maps/meal/, maphtml/meal.html) on 2026.
              12,555 rows: lat, lon (postcode-district point), ID, Year, Gender, Age, Postcode district, Meal.
              (c) the Our Dialects project, not openly licensed: individual answers are NEVER written to
              the repository; only aggregates with at least MIN_N answers are published.
  GEO/        ONS and Natural Earth boundaries: counties_uk.geojson (England ceremonial counties, Welsh
              preserved counties, Scottish council areas, Northern Ireland), uk_topo.json (ONS regions),
              lad23_bsc.geojson (local authority districts, December 2023), ne_10m_populated_places_simple.geojson.
Intermediate files (individual answers with their county and region) go to WORK, outside the repository.
"""
import json
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "/home/claude/newdata/raw"
RAW_SURVEY = os.path.join(RAW, "ourdialects_meal.json")
GEO = os.path.join(RAW, "geo")
WORK = os.environ.get("MEALWORK", "/home/claude/newdata/work/dinner-or-tea")
DATA = os.path.join(ROOT, "data")
FONT_DIR = os.environ.get("FONT_DIR", "/home/claude/ref/fonts")
for d in (WORK, DATA):
    os.makedirs(d, exist_ok=True)

SLUG = "dinner-or-tea"
TITLE = "Dinner, tea or supper? What Britain calls its evening meal"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
MIN_N = 10      # publication threshold for any aggregate cell
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

WORDS = ["dinner", "tea", "supper"]
COLOR = {"dinner": "#2E5E8C", "tea": "#B4552B", "supper": "#7A5A9E"}
COLOR_DARK = {"dinner": "#6E9FD0", "tea": "#E0814F", "supper": "#A88BCB"}
BG = "#F7F2E8"      # tablecloth cream
FG = "#24201B"
MUTED = "#73695C"
RULE = "#E4DACA"
LAND = "#ECE4D5"
MID = "#EFE6D3"     # the neutral middle of the dinner to tea ramp
LINE = "#1E1A16"    # the tea line

NORTH = ["North East", "North West", "Yorkshire and The Humber"]
MIDLANDS = ["East Midlands", "West Midlands"]
SOUTH = ["East of England", "London", "South East", "South West"]
ENG_REGIONS = NORTH + MIDLANDS + SOUTH
NATIONS = ["England", "Scotland", "Wales", "Northern Ireland"]


def band(region):
    if region in NORTH:
        return "North"
    if region in MIDLANDS:
        return "Midlands"
    if region in SOUTH:
        return "South"
    return region   # Scotland, Wales, Northern Ireland


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if math.isnan(float(o)) else float(o)
    return o


def jsave(obj, path, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean(obj), f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
