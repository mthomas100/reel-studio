"""Parse a run's mflux stage logs into per-image timings (CPU only).

Usage: python parse_logs.py [LOGS_DIR]
LOGS_DIR is the project's media logs folder; default $REEL_LOGS, else ~/Videos/reel-studio/too-much/logs.
"""
import os, re, sys, json
from pathlib import Path
logs = Path(sys.argv[1] if len(sys.argv) > 1 else
            os.environ.get("REEL_LOGS", "~/Videos/reel-studio/too-much/logs")).expanduser()
rows = []
for stage in ["cast", "views", "sets", "stills"]:
    txt = (logs / f"{stage}.log").read_text(errors="replace")
    for blk in txt.split("\n$ ")[1:]:
        cmd = blk.split("\n", 1)[0]
        body = blk.split("\n", 1)[1] if "\n" in blk else ""
        tool = cmd.split()[0].rsplit("/", 1)[-1]
        out = re.search(r"--output (\S+)", cmd).group(1).rsplit("/", 1)[-1]
        refs = 0
        m = re.search(r"--image-paths (.*?) --prompt", cmd)
        if m: refs = len(m.group(1).split())
        m = re.search(r"--width (\d+) --height (\d+)", cmd); w, h = map(int, m.groups())
        passes = re.findall(r"(\d+)/(\d+) \[(\d+):(\d+)<00:00", body)
        # final total per pass: the line where done==total; tqdm prints it twice, take unique by position
        totals = []
        for seg in re.split(r"  0%\|", body)[1:]:
            fin = re.findall(r"(\d+)/(\d+) \[(\d+):(\d+)<00:00,\s+([\d.]+)s/it\]", seg)
            fin = [f for f in fin if f[0] == f[1]]
            if fin: totals.append(int(fin[-1][2]) * 60 + int(fin[-1][3]))
        retries = body.count("verify failed")
        rows.append(dict(stage=stage, out=out, tool=tool, refs=refs, w=w, h=h, passes=len(totals), secs=sum(totals), retries=retries, complete=bool(totals) and len(totals) >= 1 + retries))
json.dump(rows, open(Path(__file__).with_name("too-much-timings.json"), "w"), indent=1)
for r in rows: print(r)
