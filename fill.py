"""Placeholder filling shared by the page, README, paper, blog and collage.

{{path.to.value|fmt}} reads data/results.json; names in X are derived values computed here from the
same file. Formats: int, pct0, pct1, f0, f1, f2, f3, raw. Tokens written [[DOI]] and [[BLOG_URL]]
become {{DOI}} and https://blog.tristanhotham.com/2026/10/31/dinner-or-tea/ for the publisher to fill.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

R = jload(os.path.join(DATA, "results.json"))


def pct(v, d=0):
    return f"{v * 100:.{d}f}%"


def pval(p):
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.2f}" if p >= 0.01 else f"p = {p:.3f}"


A = R["age"]["by_band"]
M = R["model"]
X = {
    "x_eryorks_tea": pct(R["counties"]["by_name"]["East Riding of Yorkshire"]["share"]["tea"]),
    "x_south_dinner_young": pct(A["South"][1]["dinner"]), "x_south_dinner_older": pct(A["South"][4]["dinner"]),
    "x_north_dinner_young": pct(A["North"][1]["dinner"]), "x_north_dinner_older": pct(A["North"][4]["dinner"]),
    "x_p_south": pval(M["age_by_band"]["South"]["p"]), "x_p_mid": pval(M["age_by_band"]["Midlands"]["p"]),
    "x_p_scot": pval(M["age_by_band"]["Scotland"]["p"]), "x_p_north": pval(M["age_by_band"]["North"]["p"]),
    "x_p_inter": pval(M["interaction"]["p"]), "x_p_yr": pval(M["main"]["yr"]["p"]), "x_p_supage": pval(M["supper"]["age10"]["p"]),
    "x_p_age_all": pval(M["main"]["age10"]["p"]),
    "x_r2_region": pct(M["pseudo_r2_region_only"] / M["main"]["pseudo_r2"]),
    "x_supper_old_south": pct(A["South"][5]["supper"]), "x_supper_young_south": pct(A["South"][1]["supper"]),
    "x_aber_supper": f"{R['counties']['by_name']['Aberdeenshire']['share']['supper'] * R['counties']['by_name']['Aberdeenshire']['n']:.0f}",
    "x_herts_dinner": pct(R["counties"]["by_name"]["Hertfordshire"]["share"]["dinner"]),
    "x_north_all": pct(R["band"]["North"]["n"] / R["survey"]["n"]),
    "x_glasgow_dinner": pct(R["places"]["Glasgow"]["dinner"]), "x_p_male": pval(M["main"]["male"]["p"]), "x_p_other": pval(M["main"]["other"]["p"]),
    "x_aber_n": str(R["counties"]["by_name"]["Aberdeenshire"]["n"]),
    "x_yg_dinner": pct(R["yougov"]["england"]["dinner"]), "x_yg_tea": pct(R["yougov"]["england"]["tea"]), "x_yg_supper": pct(R["yougov"]["england"]["supper"]),
    "x_yg_nmc": pct(R["yougov"]["north_mc"]["tea"]), "x_yg_nwc": pct(R["yougov"]["north_wc"]["tea"]),
    "x_yg_smc": pct(R["yougov"]["south_mc"]["dinner"]), "x_yg_swc": pct(R["yougov"]["south_wc"]["dinner"]),
}


def get(path):
    if path in X:
        return X[path]
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f, tex=False):
    if isinstance(v, str) and f in ("", "raw"):
        s = v
    elif f == "int": s = f"{int(round(float(v))):,}"
    elif f == "pct0": s = f"{v * 100:.0f}%"
    elif f == "pct1": s = f"{v * 100:.1f}%"
    elif f == "f0": s = f"{v:.0f}"
    elif f == "f1": s = f"{v:.1f}"
    elif f == "f2": s = f"{v:.2f}"
    elif f == "f3": s = f"{v:.3f}"
    else: s = str(v)
    if tex:
        s = s.replace("%", "\\%").replace("&", "\\&").replace("<", "$<$")
    return s


def fill(t, tex=False):
    def sub(m):
        path, _, f = m.group(1).partition("|")
        if path.strip() in ("DOI", "BLOG_URL", "DOI_URL") or path.startswith("IMG"):
            return m.group(0)
        return fmt(get(path.strip()), f.strip(), tex)
    t = re.sub(r"\{\{(.+?)\}\}", sub, t)
    return t.replace("[[DOI]]", "{{DOI}}").replace("[[BLOG_URL]]", "https://blog.tristanhotham.com/2026/10/31/dinner-or-tea/").replace("[[DOI_URL]]", "{{DOI_URL}}")


def check_visible(text, where):
    vis = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", text, flags=re.S)
    vis = re.sub(r'style="[^"]*"', "", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, (where, bad, vis[max(0, vis.find(bad) - 80): vis.find(bad) + 80])
