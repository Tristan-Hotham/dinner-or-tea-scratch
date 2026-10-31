"""Step 5. Static figures with matplotlib from data/ and WORK/fields.npz.
  release/paper/f_*.png   paper figures
  release/blog/b_*.png    blog figures, 1520 px wide
  WORK/header_map.png     map for the social card
Importable: reddit/collage.py reuses base(), balance_rgba(), draw_lines() and the fonts.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import to_rgb
from pyproj import Transformer

for f in ["IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "FrauncesVar.ttf"]:
    fm.fontManager.addfont(os.path.join(FONT_DIR, f))
SER, MONO = "Source Serif 4", "IBM Plex Mono"
DISP = fm.FontProperties(fname=os.path.join(FONT_DIR, "FrauncesVar.ttf"), weight=900)
plt.rcParams.update({"font.family": MONO, "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": FG, "xtick.color": MUTED,
                     "ytick.color": MUTED, "text.color": FG, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG})
R = jload(os.path.join(DATA, "results.json"))
F = np.load(os.path.join(WORK, "fields.npz"))
P, mask = F["P"], F["mask"]
x0, y0, cell = float(F["x0"]), float(F["y0"]), float(F["cell"])
ny, nx = mask.shape
EXT = [x0, x0 + nx * cell, y0, y0 + ny * cell]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
C = jload(os.path.join(DATA, "counties.geojson"))
LINES = jload(os.path.join(DATA, "tea_line.geojson"))
for d in ["release/paper", "release/blog"]:
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
POLYS = []
for f in C["features"]:
    g = f["geometry"]
    for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
        r = np.array(poly[0]); X, Y = TR.transform(r[:, 0], r[:, 1]); POLYS.append((X, Y))


def base(ax, xlim=(-10000, 670000), ylim=(0, 1000000), lw=.3, fill=True):
    for X, Y in POLYS:
        if fill:
            ax.fill(X, Y, color=LAND, lw=0, zorder=0)
        ax.plot(X, Y, color="#C9BBA2", lw=lw, zorder=3)
    ax.set_aspect("equal"); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis("off")


def balance_rgba():
    a, mid, b = (np.array(to_rgb(COLOR["dinner"])), np.array(to_rgb(MID)), np.array(to_rgb(COLOR["tea"])))
    t = (P[1] / np.maximum(P[0] + P[1], 1e-6))[..., None]
    lo = mid + (a - mid) * np.clip((0.5 - t) / 0.35, 0, 1)
    hi = mid + (b - mid) * np.clip((t - 0.5) / 0.35, 0, 1)
    img = np.zeros((ny, nx, 4)); img[..., :3] = np.where(t < .5, lo, hi); img[..., 3] = mask * 1.0
    return img


def supper_rgba():
    img = np.zeros((ny, nx, 4)); img[..., :3] = to_rgb(COLOR["supper"]); img[..., 3] = mask * np.clip(P[2] / .2, 0, 1) ** .8
    return img


def draw_lines(ax, lw=1.6, supper=False, tea=True):
    for f in LINES["features"]:
        c = np.array(f["geometry"]["coordinates"]); X, Y = TR.transform(c[:, 0], c[:, 1])
        if f["properties"]["kind"] == "tea_line":
            if not tea: continue
            ax.plot(X, Y, color=BG, lw=lw * 2.6, zorder=5, solid_capstyle="round"); ax.plot(X, Y, color=LINE, lw=lw, zorder=6, solid_capstyle="round")
        elif supper:
            ax.plot(X, Y, color=COLOR["supper"], lw=lw * .8, ls=(0, (3, 2)), zorder=6)


CITIES = {"London": (-0.118, 51.509), "Manchester": (-2.244, 53.481), "Newcastle": (-1.614, 54.973), "Birmingham": (-1.899, 52.486),
          "Leeds": (-1.548, 53.801), "Bristol": (-2.588, 51.454), "Cardiff": (-3.179, 51.481), "Glasgow": (-4.252, 55.861),
          "Edinburgh": (-3.188, 55.953), "Belfast": (-5.930, 54.597), "Nottingham": (-1.150, 52.954), "Norwich": (1.297, 52.630),
          "Plymouth": (-4.143, 50.375), "Aberdeen": (-2.094, 57.149), "Liverpool": (-2.983, 53.408)}


def cities(ax, names, fs=9.5, off=None):
    off = off or {}
    for n in names:
        X, Y = TR.transform(*CITIES[n]); dx, dy, ha = off.get(n, (7000, 4000, "left"))
        ax.plot([X], [Y], "o", ms=3, color=FG, zorder=8, mec=BG, mew=.8)
        ax.text(X + dx, Y + dy, n, fontsize=fs, family=MONO, color=FG, ha=ha, va="center", zorder=9,
                path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=2.5, foreground=BG)])


def save(fig, name, blog_w=1520):
    fig.savefig(os.path.join(ROOT, "release", "paper", f"f_{name}.png"), dpi=200)
    fig.savefig(os.path.join(ROOT, "release", "blog", f"b_{name}.png"), dpi=blog_w / fig.get_size_inches()[0])
    plt.close(fig)


def ramp_legend(fig, rect):
    a = fig.add_axes(rect); g = np.linspace(0, 1, 256)[None, :]
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("b", [(0, COLOR["dinner"]), (.15, COLOR["dinner"]), (.5, MID), (.85, COLOR["tea"]), (1, COLOR["tea"])])
    a.imshow(g, aspect="auto", cmap=cm, extent=[0, 1, 0, 1]); a.set_yticks([]); a.set_xticks([0, .5, 1]); a.set_xticklabels(["dinner leads", "level", "tea leads"], fontsize=9)
    for s in a.spines.values(): s.set_visible(False)


OFF = {"London": (8000, -9000, "left"), "Belfast": (-8000, 0, "right"), "Glasgow": (-8000, 0, "right"), "Cardiff": (-8000, -6000, "right"),
       "Bristol": (8000, -6000, "left"), "Liverpool": (-8000, 4000, "right"), "Plymouth": (-8000, -4000, "right"), "Birmingham": (8000, -5000, "left")}

if __name__ == "__main__":
    # 1. the main map
    fig = plt.figure(figsize=(7.6, 9.6))
    ax = fig.add_axes([0, .04, 1, .96]); base(ax, xlim=(-20000, 680000), ylim=(0, 1000000))
    ax.imshow(balance_rgba(), origin="lower", extent=EXT, zorder=2, interpolation="bilinear")
    draw_lines(ax, lw=1.7); cities(ax, list(CITIES), off=OFF)
    ax.text(30000, 120000, "Tea line: tea and\ndinner level", fontsize=9.5, color=FG, family=MONO)
    ramp_legend(fig, [.58, .06, .36, .018])
    save(fig, "map")
    fig = plt.figure(figsize=(6, 6.6)); ax = fig.add_axes([0, 0, 1, 1]); fig.patch.set_alpha(0)
    base(ax, xlim=(60000, 660000), ylim=(0, 980000), lw=.25); ax.imshow(balance_rgba(), origin="lower", extent=EXT, zorder=2, interpolation="bilinear"); draw_lines(ax, lw=1.6)
    fig.savefig(os.path.join(WORK, "header_map.png"), dpi=150, transparent=True); plt.close(fig)

    # 2. north to south profile
    pr = [p for p in R["lines"]["england_profile"] if p["n"] >= 50]
    fig, ax = plt.subplots(figsize=(7.6, 4.2)); fig.subplots_adjust(left=.09, right=.88, bottom=.16, top=.95)
    x = [p["northing_km"] for p in pr]
    for w in WORDS:
        ax.plot(x, [p[w] for p in pr], "-o", color=COLOR[w], lw=3 if w != "supper" else 2, ms=5)
        ax.text(x[-1] + 12, pr[-1][w], w, color=COLOR[w], va="center", fontsize=11, weight="medium")
    ax.axhline(.5, color=MUTED, ls=(0, (3, 3)), lw=.8)
    ax.set_ylim(0, 1); ax.set_yticks([0, .25, .5, .75, 1]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks([x[0], x[-1]]); ax.set_xticklabels(["South coast", "Scottish border"]); ax.set_xlabel("Distance north through England, 50 km bands (smoothed shares)", fontsize=10, color=MUTED)
    save(fig, "profile")

    # 3. regions
    regs = sorted(R["region"].items(), key=lambda kv: kv[1]["share"]["tea"])
    fig, ax = plt.subplots(figsize=(7.6, 5.0)); fig.subplots_adjust(left=.27, right=.9, bottom=.06, top=.97)
    for i, (n, r) in enumerate(regs):
        left = 0
        for w in ["tea", "supper", "dinner"]:
            v = r["share"][w]; ax.barh(i, v, left=left, color=COLOR[w], height=.72, edgecolor=BG, lw=.6)
            if v > .1: ax.text(left + .015, i, f"{v * 100:.0f}%", color="white", va="center", fontsize=9.5)
            left += v
        ax.text(1.01, i, f"{r['n']:,}", va="center", fontsize=9, color=MUTED)
    ax.set_yticks(range(len(regs))); ax.set_yticklabels([n for n, _ in regs], fontsize=10); ax.set_xlim(0, 1); ax.set_xticks([])
    for s in ("left", "bottom"): ax.spines[s].set_visible(False)
    ax.tick_params(left=False)
    save(fig, "regions")

    # 4. age by area
    fig, axs = plt.subplots(1, 3, figsize=(7.6, 3.6), sharey=True); fig.subplots_adjust(left=.09, right=.98, bottom=.17, top=.86, wspace=.12)
    lab = ["<18", "18", "25", "35", "50", "65+"]
    for ax, b in zip(axs, ["South", "Midlands", "North"]):
        a = R["age"]["by_band"][b]; m = R["model"]["age_by_band"][b]
        y = [g["dinner"] for g in a]; lo = [g["dinner"] - g["dinner_lo"] for g in a]; hi = [g["dinner_hi"] - g["dinner"] for g in a]
        ax.errorbar(range(6), y, yerr=[lo, hi], fmt="-o", color=COLOR["dinner"], ecolor=COLOR["dinner"] + "77", elinewidth=2.2, ms=5.5, lw=1.5)
        ax.set_title(f"{b}\nodds ratio {m['or']:.2f} per decade", fontsize=10, color=FG)
        ax.set_xticks(range(6)); ax.set_xticklabels(lab, fontsize=9); ax.set_ylim(0, 1); ax.grid(axis="y", color=RULE, lw=.8)
    axs[0].set_yticks([0, .25, .5, .75, 1]); axs[0].set_yticklabels(["0%", "25%", "50%", "75%", "100%"]); axs[0].set_ylabel("say dinner", fontsize=10)
    fig.text(.5, .02, "Age group (start of band)", ha="center", fontsize=9.5, color=MUTED)
    save(fig, "age")

    # 5. year
    yr = R["year"]["rows"]
    fig, ax = plt.subplots(figsize=(7.6, 3.8)); fig.subplots_adjust(left=.09, right=.97, bottom=.2, top=.95)
    X_ = [r["year"] for r in yr]
    ax.plot(X_, [r["std_dinner"] for r in yr], "-o", color=COLOR["dinner"], lw=2.5, ms=6, label="dinner, reweighted to the same region and age mix")
    ax.plot(X_, [r["share_dinner"] for r in yr], "o", mfc="none", mec=COLOR["dinner"], ms=6, label="dinner, raw")
    ax.plot(X_, [r["std_tea"] for r in yr], "-o", color=COLOR["tea"], lw=2.5, ms=6, label="tea, reweighted")
    ax.set_ylim(.2, .8); ax.set_yticks([.2, .4, .6, .8]); ax.set_yticklabels(["20%", "40%", "60%", "80%"]); ax.grid(axis="y", color=RULE, lw=.8)
    ax.set_xticks(X_); ax.set_xticklabels([f"{x}\n{r['n']:,}" for x, r in zip(X_, yr)], fontsize=8)
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)
    save(fig, "year")

    # 6. supper: map and age
    fig = plt.figure(figsize=(7.6, 5.4))
    ax = fig.add_axes([0, 0, .5, 1]); base(ax, xlim=(-20000, 680000), ylim=(0, 1000000), lw=.2)
    ax.imshow(supper_rgba(), origin="lower", extent=EXT, zorder=2, interpolation="bilinear"); draw_lines(ax, lw=1.0, supper=True, tea=False)
    ax.text(470000, 930000, "Share saying supper\n(darkest: 20% or more)", fontsize=9, color=MUTED)
    a2 = fig.add_axes([.58, .16, .4, .72])
    G = ["<18", "18", "25", "35", "50", "65+"]
    for b, ls in (("South", "-"), ("Midlands", "--"), ("North", ":")):
        a2.plot(range(6), [g["supper"] for g in R["age"]["by_band"][b]], ls, marker="o", color=COLOR["supper"], lw=2, ms=4.5, label=b)
    a2.set_xticks(range(6)); a2.set_xticklabels(G, fontsize=9); a2.set_yticks([0, .05, .1, .15, .2]); a2.set_yticklabels(["0%", "5%", "10%", "15%", "20%"])
    a2.set_title("say supper, by age", fontsize=10); a2.legend(frameon=False, fontsize=9); a2.grid(axis="y", color=RULE, lw=.8)
    save(fig, "supper")

    # 7. YouGov check
    E, Y = R["england_check"], R["yougov"]["england"]
    fig, ax = plt.subplots(figsize=(7.6, 3.4)); fig.subplots_adjust(left=.22, right=.97, bottom=.12, top=.95)
    rows = [("YouGov 2018", Y), ("Survey, reweighted", E["weighted"]), ("Survey, raw", E["raw"])]
    for i, (n, s) in enumerate(rows[::-1]):
        left = 0
        for w in ["dinner", "supper", "tea"]:
            ax.barh(i, s[w], left=left, color=COLOR[w], height=.6, edgecolor=BG)
            if s[w] > .08: ax.text(left + .015, i, f"{w} {s[w] * 100:.0f}%", color="white", va="center", fontsize=9.5)
            left += s[w]
    ax.set_yticks(range(3)); ax.set_yticklabels([r[0] for r in rows[::-1]]); ax.set_xlim(0, 1); ax.set_xticks([])
    for s in ("left", "bottom"): ax.spines[s].set_visible(False)
    ax.tick_params(left=False)
    save(fig, "yougov")
    print("figures written")
