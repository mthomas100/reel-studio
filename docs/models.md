# Which local model runs each stage (M5 Max, 128 GB, chosen 2026-10-04)

The model scout's choices for each stage of the still-first workflow, run fully locally on Apple Silicon. Arena
numbers are Artificial Analysis (AA) leaderboards read on 2026-10-04; "measured" means measured on this Mac
(`docs/test-runs.md`); anything else is marked as an estimate or a vendor claim. Change a model in `config.toml`,
never in `bin/reel`.

## The stack

| stage | model | runs as | size | licence | measured here |
|---|---|---|---|---|---|
| hero stills, set plates | **Qwen-Image-2.1** | `mflux-generate-qwen-2.1` (mflux 0.21, MLX) | 33 GB bf16 | Qwen Research Licence (non-commercial) | ~45 s per 704x1280 still at 40 steps; ~280 s per 1408x2560 set plate |
| identity views + every shot's still | **Qwen-Image-2.1 edit**, up to 10 references, `--verify` with Qwen3-VL | `mflux-generate-qwen-2.1-edit` | same weights | same | 83-120 s per still with 3-5 references; double that when the verifier retries |
| draft edits (optional) | Qwen-Image-2.1 + Viggle turbo LoRA (6 steps) | `[edit.profiles.qwen-turbo]` | +1.4 GB | Qwen Research | not used in the test reels |
| fast fallback edit | FLUX.2 klein 4B | `mflux-generate-flux2-edit` | 7.2 GB | Apache-2.0 | 21-40 s per still, but it duplicated a person at 5 references |
| image-to-video | **LTX-2.5** (q8 MLX pack) on ltx-2-mlx | `vidgen -i still.png` from local-video | 75 GB | LTX-2 Community License (free under $10M revenue) | mean 111 s per clip; 73 s for 3 s, 366 s for 10 s (704x1280, fast mode) |
| narrator and character voices | **Qwen3-TTS 12 Hz 1.7B VoiceDesign** (10 languages incl. English and Russian) | mlx-audio | 4.5 GB | Apache-2.0 | 14 s for 11 lines |
| music bed | **MiniMax-Music3** mxfp8 | `python -m mlx_audio.music.generate` | 13.9 GB | MiniMax-Music3 Community Licence | 109 s for one bed |
| speech check | whisper large-v3-turbo (q5_0) | whisper.cpp `whisper-cli`, CPU | 0.6 GB | MIT | — |
| teardown stems (bin/reverse) | HTDemucs | Demucs, CPU | small | MIT | — |
| agent director (optional) | Qwen3.8 Flash Next (vision) or DeepSeek V4 Flash Vision | pi on a local llama-server | — | per model | pi smoke test passed in 84 s |

## Why these, and not the others

- **Stills: Qwen-Image-2.1** was the #1 open-weights model in both AA image arenas (text-to-image Elo 1036;
  editing Elo 1073). mflux 0.21.0 (2026-10-03) added the 2.1 edit command with up to 10 reference images, which is
  what makes "the same people in every shot" possible locally.
  - An A/B on three shots against FLUX.2 klein 4B: klein is 4-5x faster, but with five references it duplicated a
    person and recoloured the extras; Qwen got that shot right. Qwen is the default, klein a draft profile.
  - Alternates looked at: Krea 2 Turbo (gated, 62 GB), Z-Image Turbo (fast, less world knowledge), Ideogram 4
    (typography-first), FLUX.2 [dev] (no MLX port, 177 GB), HunyuanImage 3.0 (PyTorch only).
- **Video: LTX-2.5.** It sits just behind Kling 3.0 Pro on the AA image-to-video board (LTX-2.5 Fast 1038, Kling
  1055) and has a working MLX runtime.
  - MiniMax-H3 scores higher (1181) and has a 9-image reference mode, but its licence lists the USA, EU, UK and Korea
    as excluded territories, so it was ruled out.
  - MAGI-2 is 307 GB with no Mac runtime; Wan 2.2 and HunyuanVideo 1.5 have no maintained MLX path.
  - LTX's reference-sheet IC-LoRA ("Ingredients") is gated and not yet supported by ltx-2-mlx.
- **Voice: Qwen3-TTS VoiceDesign.** Designs a voice from a sentence, speaks 10 languages, already runs on MLX.
- **Music: MiniMax-Music3.** The anchor (Elo 1000) of both AA music arenas and the only open-weights model on both
  boards that does full songs; its licence has no territory exclusion. Alternates: Stable Audio 3 Medium
  (instrumental only, gated), ACE-Step 1.5 (MIT).

## Memory and scheduling

Qwen edit (about 31 GB), LTX-2.5 at 704x1280 (45-53 GB) and a local vision LLM (80-90 GB) cannot all be resident
at once, so stages run one at a time. On the author's Mac every GPU stage runs inside a GPU hold (`hold run`, from
local-rig) that queues behind other renders and unloads the local LLM while the stage runs.

## Open risks

1. LTX-2.5 redraws faces as it animates: perfect stills can still drift in the clip. Keep motion small and takes short.
2. Several licences are **non-commercial** (Qwen-Image-2.1, the Viggle LoRA): fine for personal reels, not for paid
   work.
3. MiniMax-Music3's tempo and key control is loose; check the bed with a beat/key detector.
4. The edit verifier is noisy (it fails many good edits) and blind to the commonest real failure (a doubled
   person). The contact-sheet review is the real gate.

## Sources (read 2026-10-04)

- AA leaderboards: https://artificialanalysis.ai/image/leaderboard/text-to-image/open-weights ,
  https://artificialanalysis.ai/image/leaderboard/editing/open-weights ,
  https://artificialanalysis.ai/video/leaderboard/image-to-video ,
  https://artificialanalysis.ai/music/leaderboard/instrumental
- mflux 0.21.0: https://github.com/mflux-community/mflux/releases ; Viggle scheduler:
  https://github.com/mflux-community/mflux/pull/764
- Qwen-Image-2.1 https://huggingface.co/Qwen/Qwen-Image-2.1 ; Viggle turbo
  https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo
- LTX-2.5 https://huggingface.co/Lightricks/LTX-2.5 ; ltx-2-mlx https://github.com/dgrauet/ltx-2-mlx
- MiniMax-H3 licence https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
- MiniMax-Music3 https://huggingface.co/MiniMaxAI/MiniMax-Music3 , https://huggingface.co/mlx-community/MiniMax-Music3-mxfp8
- Qwen3-TTS https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign , https://github.com/QwenLM/Qwen3-TTS
- whisper.cpp https://github.com/ggerganov/whisper.cpp ; Demucs https://github.com/facebookresearch/demucs
