#!/usr/bin/env bash
# setup.sh — rebuild everything reel-studio needs that is not in git (2026-10-04). Safe to re-run.
# Weights go to ~/.cache/huggingface (shared with the film rig); nothing here touches the local-video checkout.
set -euo pipefail
cd "$(dirname "$0")"

# 1. Our own venv: mflux 0.21.0 adds mflux-generate-qwen-2.1-edit (up to 10 references). The film rig pins 0.20
#    in its own venv, so reel-studio never upgrades that one.
[ -x .venv/bin/python ] || uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python "mflux==0.21.0" huggingface_hub numpy pillow

# 2. Weights (docs/models.md says why each one). Qwen-Image-2.1 is about 33 GB; skipped if already cached.
.venv/bin/hf download Qwen/Qwen-Image-2.1 >/dev/null
.venv/bin/hf download Viggle/Qwen-Image-2.1-viggle-turbo Qwen-Image-2.1-viggle-turbo-v0.2.1-6step-lora-r256.safetensors >/dev/null
.venv/bin/hf download mlx-community/MiniMax-Music3-mxfp8 >/dev/null          # music bed, run by mlx-audio's venv

# 3. Shared tools this studio calls but does not own (each has its own recipe). By default config.toml expects
#    them cloned NEXT TO this repo (../local-video, ../mlx-audio, ../local-rig); change [paths] to move them.
#    ../local-video/bin/vidgen          LTX-2.5 image-to-video (github.com/mthomas100/local-video, its setup.sh)
#    ../mlx-audio/.venv                 Qwen3-TTS VoiceDesign + MiniMax-Music3 code (github.com/Blaizzy/mlx-audio)
#    ~/.cache/local-video/sync-venv     Demucs, parselmouth, librosa for bin/reverse (local-video's sync setup;
#                                       or point REVERSE_PYTHON at any Python that has them)
#    whisper-cli + ~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin   transcripts (brew install whisper-cpp)
#    hold                               the Mac's GPU lock (github.com/mthomas100/local-rig); optional: without it
#                                       GPU stages simply run, so never start two at once
mkdir -p ~/.cache/whisper-cpp
[ -f ~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin ] || curl -sL -o ~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin

# 4. Skills, linked for Claude Code and pi (names start with reel- so they never shadow the film rig's skills).
mkdir -p ~/.claude/skills
for s in skills/*/; do
  n=$(basename "$s")
  ln -sfn "$PWD/$s" ~/.claude/skills/"$n"
  [ -d ~/.pi/agent/skills ] && ln -sfn "$PWD/$s" ~/.pi/agent/skills/"$n"
done
echo "reel-studio ready: bin/reel, bin/reverse; skills: $(ls skills | tr '\n' ' ')"
