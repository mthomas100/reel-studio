#!/usr/bin/env python3
"""voice.py — the reel's voice track on the reel's own clock (2026-10-04). Run by `reel voice` inside the GPU hold.

Qwen3-TTS 1.7B VoiceDesign on MLX (mlx-audio's venv). Unlike the film rig's tts.py it takes the language from the
project (the model's table: chinese, english, german, italian, portuguese, spanish, japanese, korean, french,
russian), so a reel can be narrated in any of them. Each line is designed from a persona (the
narrator's, or the line's own `voice`) plus the line's delivery, trimmed, and placed at its `start` second.
Every take is checked by whisper (CPU) against the script and re-spoken with a new seed (up to 3 tries) when the
words come out wrong; a line that runs into the next is sped up (at most 1.35x, pitch kept), and any overlap left is
reported, never silently cut. (2026-10-04: a one-word shout came out as a different word; a slow delivery ran 8 s
against a 3.3 s slot.)

  voice.py <spec.json>    spec: {lang, persona, seed, out, lines: [{start, text, delivery, voice?}]}
"""
from __future__ import annotations
import difflib, json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, soundfile as sf
import mlx.core as mx
from mlx_audio.tts.utils import load_model

MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16"
SR_OUT = 48000
WHISPER = Path.home() / ".cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin"
WHISPER_LANG = {"english": "en", "russian": "ru", "german": "de", "french": "fr", "spanish": "es", "italian": "it",
                "portuguese": "pt", "japanese": "ja", "korean": "ko", "chinese": "zh"}
TRIES = 3            # a line whose words come out wrong is spoken again with a new seed (machine-checked, no listening)
MATCH_OK = 0.8       # word-level similarity between the script and whisper's transcript of the take
MAX_TEMPO = 1.35     # a line that runs into the next is sped up by at most this much, as an editor would

def words(t: str) -> list[str]:
    return re.findall(r"[\w']+", t.lower())

def heard(w: np.ndarray, sr: int, lang: str) -> str:
    """What whisper (CPU) hears in a take; '' if whisper is not installed."""
    if not WHISPER.exists():
        return ""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "l.wav"
        x = np.interp(np.arange(0, len(w), sr / 16000), np.arange(len(w)), w).astype(np.float32)
        sf.write(f, x, 16000)
        r = subprocess.run(["whisper-cli", "-ng", "-t", "8", "-nt", "-m", str(WHISPER), "-l", WHISPER_LANG.get(lang, "auto"),
                            "-f", str(f)], capture_output=True, text=True)
        return " ".join(l.strip() for l in r.stdout.splitlines() if l.strip())

def match(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, words(a), words(b)).ratio() if b else 1.0

def tempo(w: np.ndarray, sr: int, factor: float) -> np.ndarray:
    """Speed speech up without changing its pitch (ffmpeg atempo)."""
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / "a.wav", Path(d) / "b.wav"
        sf.write(a, w, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-af", f"atempo={factor:.3f}", str(b)], check=True)
        y, _ = sf.read(b, dtype="float32")
        return y

def trim(w: np.ndarray, sr: int, db: float = -40) -> np.ndarray:
    env = np.abs(w); idx = np.where(env > np.max(env) * 10 ** (db / 20))[0]
    if not len(idx):
        return w
    k = int(0.03 * sr)
    return w[max(0, idx[0] - k):idx[-1] + k]

def main() -> None:
    spec = json.loads(Path(sys.argv[1]).read_text())
    out = Path(spec["out"]); lines = spec["lines"]; lang = spec.get("lang", "english")
    tts = load_model(MODEL)
    placed, report = [], []
    for i, ln in enumerate(lines):
        persona = ln.get("voice") or spec["persona"]
        text = ln["text_ru"] if lang == "russian" and ln.get("text_ru") else ln["text"]
        best = None
        for t in range(TRIES):
            mx.random.seed(int(spec.get("seed", 7)) + i + 101 * t)
            parts, sr = [], 24000
            for r in tts.generate(text, instruct=f"{persona}. {ln.get('delivery', '')}".strip(), lang_code=lang,
                                  max_tokens=int(len(text) * 2.2) + 60):
                parts.append(np.asarray(r.audio, dtype=np.float32)); sr = r.sample_rate
            mx.clear_cache()
            w = trim(np.concatenate(parts), sr) if parts else np.zeros(1, np.float32)
            got = heard(w, sr, lang); score = match(text, got)
            if best is None or score > best[0]:
                best = (score, w, sr, got, t + 1)
            if score >= MATCH_OK:
                break
        score, w, sr, got, tries = best
        # fit: never run into the next line (or past the reel's end) when a modest speed-up can avoid it
        nxt = [float(x["start"]) for x in lines[i + 1:]] + [float(spec.get("length", 0)) or 1e9]
        room = min(nxt) - float(ln["start"]) - 0.08
        sped = 1.0
        if len(w) / sr > room > 0:
            sped = min(MAX_TEMPO, (len(w) / sr) / room)
            w = tempo(w, sr, sped)
        sf.write(out / f"line-{i + 1:02d}.wav", w, sr)
        placed.append((float(ln["start"]), w, sr))
        report.append({"n": i + 1, "start": ln["start"], "secs": round(len(w) / sr, 2), "text": text, "heard": got,
                       "match": round(score, 2), "tries": tries, "tempo": round(sped, 2)})
    total = max(s + len(w) / sr for s, w, sr in placed) + 0.5
    total = max(total, float(spec.get("length", 0)))
    mixbuf = np.zeros(int(total * SR_OUT), np.float32)
    for k, (s, w, sr) in enumerate(placed):
        x = np.interp(np.arange(0, len(w), sr / SR_OUT), np.arange(len(w)), w).astype(np.float32)
        a = int(s * SR_OUT); mixbuf[a:a + len(x)] += x[: len(mixbuf) - a]
        nxt = placed[k + 1][0] if k + 1 < len(placed) else None
        report[k]["end"] = round(s + len(w) / sr, 2)
        if nxt is not None and s + len(w) / sr > nxt:
            report[k]["overlaps_next_by"] = round(s + len(w) / sr - nxt, 2)
    mixbuf = mixbuf / (np.max(np.abs(mixbuf)) + 1e-9) * 0.8
    sf.write(out / "narration.wav", np.stack([mixbuf, mixbuf], 1), SR_OUT)
    (out / "narration.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for r in report:
        flag = f"  OVERLAPS NEXT by {r['overlaps_next_by']} s" if "overlaps_next_by" in r else ""
        print(f"  line {r['n']}: {r['start']:>5}-{r['end']:<6} match {r['match']} ({r['tries']} tries"
              f"{', x' + str(r['tempo']) if r['tempo'] > 1 else ''}) {r['text']}{flag}")
        if r["match"] < MATCH_OK:
            print(f"    WORDS OFF: heard {r['heard']!r}; rewrite the line or its delivery")
    print(f"  wrote {out / 'narration.wav'}")

if __name__ == "__main__":
    main()
