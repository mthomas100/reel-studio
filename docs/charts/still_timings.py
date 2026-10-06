from pathlib import Path
import json, random
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [r for r in json.load(open(Path(__file__).with_name("too-much-timings.json"))) if r["complete"]]
def cat(r):
    if r["stage"] == "sets": return "set plate, 1408x2560\n(text-to-image)"
    if r["stage"] == "cast": return "cast portrait, 1024x1536\n(text-to-image)"
    if r["stage"] == "views": return "identity view, 1024x1024\n(edit, 1 reference)"
    if r["refs"] == 0: return "shot still, 704x1280\n(text-to-image)"
    return f"shot still, 704x1280\n(edit, {r['refs']} references)"
order = ["cast portrait, 1024x1536\n(text-to-image)", "identity view, 1024x1024\n(edit, 1 reference)",
         "set plate, 1408x2560\n(text-to-image)", "shot still, 704x1280\n(text-to-image)",
         "shot still, 704x1280\n(edit, 3 references)", "shot still, 704x1280\n(edit, 5 references)"]
order = [o for o in order if any(cat(r) == o for r in rows)]
TXT, TXT2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C = {False: "#2a78d6", True: "#eb6834"}
plt.rcParams.update({"font.family": "Helvetica", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 5.4), dpi=160, facecolor=SURF); ax.set_facecolor(SURF)
random.seed(3)
for i, o in enumerate(order):
    rs = [r for r in rows if cat(r) == o]
    for retried in (False, True):
        xs = [r["secs"] for r in rs if bool(r["retries"]) == retried]
        ys = [len(order) - 1 - i + random.uniform(-0.18, 0.18) for _ in xs]
        ax.scatter(xs, ys, s=46, color=C[retried], edgecolor=SURF, linewidth=1.5, zorder=3,
                   label=("verifier failed, edit re-run once" if retried else "first pass") if i == 4 else None)
    n, k = len(rs), sum(1 for r in rs if r["retries"])
    lab = f"n={n}" + (f", {k} retried" if "edit" in o else "")
    ax.text(max(r["secs"] for r in rs) + 8, len(order) - 1 - i, lab, va="center", color=TXT2, fontsize=9.5)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order[::-1], color=TXT, fontsize=9.5)
ax.set_xlabel("seconds per image (sum of diffusion passes, from the mflux progress bars)", color=TXT2)
ax.set_xlim(0, 320); ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(colors=TXT2, length=0)
ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=TXT)
ax.set_title("too-much: time per generated image on an M5 Max (Qwen-Image-2.1, 40 steps)", loc="left", color=TXT, fontsize=12.5, pad=12)
fig.text(0.01, 0.01, "Data: logs/{cast,views,sets,stills}.log of the too-much run, 2026-10-05 18:24-21:37 (run still in progress; "
         "in-flight images excluded). Model load time not included.", color=TXT2, fontsize=8)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(Path(__file__).parent.parent / "media/still-timings.png", facecolor=SURF)
