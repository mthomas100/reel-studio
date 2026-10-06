#!/usr/bin/env bash
# music.sh — a music bed from a caption with MiniMax-Music3 (mxfp8, MLX, mlx-audio's venv) (2026-10-04).
# Called by `reel music` inside the GPU hold. Instrumental unless --lyrics is given (section-tagged lines).
#   music.sh --prompt "<style, instruments, bpm, key>" --seconds 62 --seed 1 --output music.wav [--lyrics "..."]
set -euo pipefail
# mlx-audio's venv: MLX_AUDIO_PYTHON, else a mlx-audio checkout cloned next to this repo
PY=${MLX_AUDIO_PYTHON:-$(cd "$(dirname "$0")/../.." && pwd)/mlx-audio/.venv/bin/python}
MODEL=mlx-community/MiniMax-Music3-mxfp8
prompt="" secs=60 seed=1 out="" lyrics="[instrumental]"
while [ $# -gt 0 ]; do case "$1" in
  --prompt) prompt="$2"; shift 2;; --seconds) secs="$2"; shift 2;; --seed) seed="$2"; shift 2;;
  --output) out="$2"; shift 2;; --lyrics) lyrics="$2"; shift 2;; *) echo "music.sh: unknown $1" >&2; exit 2;; esac
done
raw="${out%.*}-raw.wav"
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
# --duration is only an upper bound: the model may end early (2026-10-04: 38 s of a requested 62). Try up to 3 seeds,
# keep the longest, then loop the piece with 2 s crossfades until it covers the reel, and fade out at the end.
best=0
for k in 0 1 2; do
  try="${out%.*}-try$k.wav"
  "$PY" -m mlx_audio.music.generate --model "$MODEL" --caption "$prompt" --lyrics "$lyrics" --duration "$secs" \
    --seed $((seed + k)) --output "$try" --verbose
  d=$(dur "$try"); echo "music.sh: seed $((seed + k)) gave ${d} s"
  if python3 -c "import sys; sys.exit(0 if $d > $best else 1)"; then best=$d; cp "$try" "$raw"; fi
  python3 -c "import sys; sys.exit(0 if $d >= 0.8 * $secs else 1)" && break
done
cur="$raw"; n=0
while python3 -c "import sys; sys.exit(0 if $(dur "$cur") < $secs else 1)"; do
  n=$((n + 1)); nxt="${out%.*}-loop$n.wav"
  ffmpeg -v error -y -i "$cur" -i "$raw" -filter_complex "acrossfade=d=2:c1=tri:c2=tri" "$nxt"; cur="$nxt"
done
[ $n -gt 0 ] && echo "music.sh: looped the piece $n time(s) to cover ${secs} s"
# 48 kHz stereo, loudness-normalised so the cut's gain_db means the same thing for every bed; 2 s fade at the end
ffmpeg -v error -y -i "$cur" -af "atrim=duration=${secs},afade=t=out:st=$(python3 -c "print(max(0, $secs - 2))"):d=2,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -ac 2 "$out"
echo "music.sh: wrote $out"
