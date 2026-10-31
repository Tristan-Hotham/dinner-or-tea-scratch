"""Step 7. Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_Dinner_Tea_or_Supper.tex and .pdf (figures f_*.png from 05_figures.py)."""
import sys, os, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Dinner_Tea_or_Supper"
E = R["england_check"]
rows = ""
for reg in ENG_REGIONS + ["Wales", "Scotland", "Northern Ireland"]:
    r = R["region"][reg]
    samp = f"{E['sample_share'][reg] * 100:.1f}" if reg in E["sample_share"] else ""
    pop = f"{E['pop_share'][reg] * 100:.1f}" if reg in E["pop_share"] else ""
    rows += f"{reg} & {r['n']:,} & {samp} & {pop} & {r['share']['dinner'] * 100:.1f} & {r['share']['tea'] * 100:.1f} & {r['share']['supper'] * 100:.1f}\\\\\n"
TR_ = ("\\begin{table}[tbp]\\centering\\small\\caption{Answers by region. Sample and population columns: share of England's answers and of England's population (Census 2021), per cent.}\\label{tab:regions}"
       "\\begin{tabular}{lrrrrrr}\\toprule Region & Answers & \\% of sample & \\% of pop. & Dinner \\% & Tea \\% & Supper \\%\\\\\\midrule\n" + rows +
       f"\\midrule All & {R['survey']['n']:,} & & & {R['survey']['share']['dinner'] * 100:.1f} & {R['survey']['share']['tea'] * 100:.1f} & {R['survey']['share']['supper'] * 100:.1f}\\\\\\bottomrule\\end{{tabular}}\\end{{table}}")
M_ = R["model"]["main"]
ci = lambda o: f"{o['or']:.2f} & {o['lo']:.2f} to {o['hi']:.2f} & {pval(o['p']).replace('p ', '').replace('< ', '$<$ ').replace('= ', '')}"
mrows = f"Age (per decade) & {ci(M_['age10'])}\\\\\nSurvey year (per year) & {ci(M_['yr'])}\\\\\nMale (against female) & {ci(M_['male'])}\\\\\nOther or not given & {ci(M_['other'])}\\\\\n\\midrule\n"
for reg, o in M_["regions"].items():
    mrows += f"{reg} & {ci(o)}\\\\\n"
TM = ("\\begin{table}[tbp]\\centering\\small\\caption{Logistic regression of saying dinner rather than tea (n = " + f"{R['model']['n']:,}" + "). Odds ratios with 95\\% intervals; regions against the North West. McFadden pseudo R\\textsuperscript{2} " + f"{M_['pseudo_r2']:.3f}" + ".}\\label{tab:model}"
      "\\begin{tabular}{lrrr}\\toprule Term & Odds ratio & 95\\% interval & p\\\\\\midrule\n" + mrows + "\\bottomrule\\end{tabular}\\end{table}")
arows = ""
for b in ["North", "Midlands", "South", "Scotland", "Wales", "Northern Ireland"]:
    o = R["model"]["age_by_band"][b]
    arows += f"{b} & {o['n']:,} & {ci(o)}\\\\\n"
TA = ("\\begin{table}[tbp]\\centering\\small\\caption{Age slope for dinner against tea, fitted separately in each area (with survey year, gender and, where there is more than one, region). Odds ratio per decade of age; below 1, younger people say dinner more.}\\label{tab:age}"
      "\\begin{tabular}{lrrrr}\\toprule Area & Answers & Odds ratio & 95\\% interval & p\\\\\\midrule\n" + arows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{TABLE_REGIONS}}", TR_).replace("{{TABLE_MODEL}}", TM).replace("{{TABLE_AGE}}", TA)
t = re.sub(r"\\url\{\{\{(meta\.\w+)\|raw\}\}\}", lambda m: "\\url{" + get(m.group(1)) + "}", t)
t = fill(t, tex=True)
assert "[[" not in t and "\u2014" not in t and "\u2013" not in t and "--" not in t.replace("{{DOI}}", "")
assert re.findall(r"\{\{(?!DOI)", t) == [], re.findall(r"\{\{.{0,30}", t)[:5]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013"))
