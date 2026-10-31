"""r/dataisbeautiful collage: Dinner, tea or supper? 2400 x 3000 px, light tablecloth background.
Run: python3 reddit/collage.py (after code/02_analyse.py). Numbers from data/results.json."""
import importlib.util, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("figs", os.path.join(ROOT, "code", "05_figures.py"))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
plt, R, COLOR, BG, FG, MUTED, DISP, SER, MONO = F.plt, F.R, F.COLOR, F.BG, F.FG, F.MUTED, F.DISP, F.SER, F.MONO
import matplotlib.patheffects as pe
B, N, M, A = R["band"], R["nation"], R["model"], R["age"]["by_band"]
pc = lambda v: f"{v * 100:.0f}%"

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
x = .045
for word, col in (("Dinner, ", COLOR["dinner"]), ("tea", COLOR["tea"]), (" or ", FG), ("supper?", COLOR["supper"])):
    t = fig.text(x, .968, word, fontproperties=DISP, fontsize=50, color=col, va="top")
    x = t.get_window_extent(renderer=fig.canvas.get_renderer()).transformed(fig.transFigure.inverted()).x1
fig.text(.045, .912, f"What Britain calls its evening meal: {R['survey']['n']:,} answers to the Our Dialects survey ({R['survey']['year_min']} to {R['survey']['year_max']}),\n"
         "smoothed into a map, with the tea line where tea and dinner are level.", family=SER, fontsize=15, color=FG, va="top", linespacing=1.4)

ax = fig.add_axes([0.0, .30, .6, .585])
F.base(ax, xlim=(-40000, 680000), ylim=(0, 1000000), lw=.3)
ax.imshow(F.balance_rgba(), origin="lower", extent=F.EXT, zorder=2, interpolation="bilinear")
F.draw_lines(ax, lw=1.6)
F.cities(ax, ["London", "Manchester", "Newcastle", "Birmingham", "Glasgow", "Belfast", "Cardiff", "Leeds"], fs=10, off=F.OFF)
stroke = [pe.withStroke(linewidth=3, foreground=BG)]
# labels on the sea only
ax.text(598000, 590000, "TEA\nnorth of\nEngland\n" + pc(B["North"]["share"]["tea"]) + " tea", fontsize=12, family=MONO, color=COLOR["tea"], ha="center", va="center", weight="medium", path_effects=stroke)
ax.text(560000, 60000, "DINNER\nsouth of England\n" + pc(B["South"]["share"]["dinner"]) + " dinner", fontsize=12, family=MONO, color=COLOR["dinner"], ha="center", va="center", weight="medium", path_effects=stroke)
ax.text(70000, 340000, "Wales\n" + pc(N["Wales"]["share"]["tea"]) + " tea", fontsize=11, family=MONO, color=COLOR["tea"], ha="center", va="center", path_effects=stroke)
ax.text(40000, 450000, "Northern Ireland\n" + pc(N["Northern Ireland"]["share"]["dinner"]) + " dinner", fontsize=11, family=MONO, color=COLOR["dinner"], ha="center", va="center", path_effects=stroke)
ax.text(560000, 860000, "Scotland\n" + pc(N["Scotland"]["share"]["dinner"]) + " dinner", fontsize=11, family=MONO, color=COLOR["dinner"], ha="center", va="center", path_effects=stroke)
ax.text(30000, 150000, "The tea line\n(black): tea and\ndinner level", fontsize=10.5, family=MONO, color=FG, ha="left", va="center", path_effects=stroke)

# legend
lg = fig.add_axes([.6, .745, .37, .08]); lg.axis("off")
g = np.linspace(0, 1, 256)[None, :]
from matplotlib.colors import LinearSegmentedColormap
cm = LinearSegmentedColormap.from_list("b", [(0, COLOR["dinner"]), (.15, COLOR["dinner"]), (.5, F.MID), (.85, COLOR["tea"]), (1, COLOR["tea"])])
lg.imshow(g, aspect="auto", cmap=cm, extent=[0, 1, .55, .85], transform=lg.transAxes)
lg.set_xlim(0, 1); lg.set_ylim(0, 1)
lg.text(0, .4, "dinner leads", family=MONO, fontsize=11, color=COLOR["dinner"], va="top")
lg.text(.5, .4, "level", family=MONO, fontsize=11, color=MUTED, va="top", ha="center")
lg.text(1, .4, "tea leads", family=MONO, fontsize=11, color=COLOR["tea"], va="top", ha="right")
lg.text(0, 1.05, "Smoothed share of the two leading words", family=MONO, fontsize=10.5, color=MUTED)

tx = fig.add_axes([.6, .30, .37, .41]); tx.axis("off")
notes = [(pc(B["North"]["share"]["tea"]), COLOR["tea"], f"of {B['North']['n']:,} answers from the north of\nEngland say tea. The Midlands split\n{pc(B['Midlands']['share']['tea'])} tea, {pc(B['Midlands']['share']['dinner'])} dinner."),
         (pc(B["South"]["share"]["dinner"]), COLOR["dinner"], f"of {B['South']['n']:,} answers from the south say\ndinner. London: only {pc(R['london']['share']['tea'])} tea."),
         (f"{M['age_by_band']['North']['or']:.2f}", FG, f"odds ratio for dinner per decade of age in\nthe north: no age gap at all.\nIn the south {M['age_by_band']['South']['or']:.2f}: the young say dinner more."),
         (pc(A["South"][5]["supper"]), COLOR["supper"], f"of southerners aged 65+ say supper,\nagainst {pc(A['South'][1]['supper'])} of 18 to 24s. Overall supper\nis {R['survey']['share']['supper'] * 100:.1f}%.")]
for (big, col, small), y in zip(notes, [1.0, .75, .5, .25]):
    tx.text(0, y, big, fontproperties=DISP, fontsize=30, color=col, va="top", transform=tx.transAxes)
    tx.text(0, y - .085, small, family=SER, fontsize=12.5, color=FG, va="top", transform=tx.transAxes, linespacing=1.3)

fig.text(.045, .275, "SHARE SAYING DINNER, BY AGE (95% intervals)", family=MONO, fontsize=11, color=MUTED)
lab = ["<18", "18-24", "25-34", "35-49", "50-64", "65+"]
for i, b in enumerate(["South", "Midlands", "North"]):
    a = fig.add_axes([.07 + i * .31, .085, .26, .16])
    y = [g_["dinner"] for g_ in A[b]]
    a.errorbar(range(6), y, yerr=[[g_["dinner"] - g_["dinner_lo"] for g_ in A[b]], [g_["dinner_hi"] - g_["dinner"] for g_ in A[b]]],
               fmt="-o", color=COLOR["dinner"], ecolor=COLOR["dinner"] + "66", elinewidth=2.2, ms=5, lw=1.6)
    a.set_ylim(0, 1); a.set_yticks([0, .5, 1]); a.set_yticklabels(["0%", "50%", "100%"] if i == 0 else ["", "", ""], fontsize=9.5)
    a.set_xticks(range(6)); a.set_xticklabels(lab, fontsize=8.5); a.grid(axis="y", color=F.RULE, lw=.8)
    a.set_title(f"{b} of England" if b != "Midlands" else "Midlands", fontsize=11.5, color=FG, family=MONO)

fig.text(.045, .014,
         "Data: Our Dialects meal map (ourdialects.uk, University of Manchester), answers used with credit and aggregated only. Boundaries and\n"
         "Census 2021: ONS (OGL v3). Check: YouGov 2018. Smoothing: Gaussian kernel, " + f"{R['smoothing']['cv_best_km']} km" + " where answers are dense (cross-validated).\n"
         "Analysis and chart: Tristan Hotham, Python and matplotlib. Interactive map: maps.tristanhotham.com/dinner-or-tea",
         family=MONO, fontsize=9, color=MUTED, linespacing=1.45)
fig.savefig(os.path.join(HERE, "dinner_or_tea.png"), facecolor=BG, dpi=200)
print("ok")
