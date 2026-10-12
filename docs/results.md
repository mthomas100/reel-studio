# Measured results

All on one Apple Silicon Mac (M5 Max, 128 GB unified memory). Times are wall-clock from the stage logs. The README's
[Measurements](../README.md#measurements) section summarises these; the per-image chart is built from
`docs/charts/too-much-timings.json`.

## First end-to-end test (2026-10-04/05)

A 25-shot, 61.25 s test project with four recurring characters (704x1280). Its project file and media are not part
of this repo.

| stage | model / command | measured |
|---|---|---|
| cast portraits, 1024x1536, 40 steps | Qwen-Image-2.1 (mflux 0.20) | ~2 min an image; 8 portraits in ~16 min |
| set plates, 1408x2560, 40 steps | Qwen-Image-2.1 | ~5 min a plate |
| identity views, 1024x1024, `--verify --verify-retries 1` | Qwen-Image-2.1 edit (mflux 0.21.0) | 81-86 s a view (12 in ~17 min). The verifier failed about a third on "outside_unchanged" and retried once. **Identity held** across face, three-quarter and profile views of all four characters. |
| editor A/B on 3 shots | Qwen-2.1 edit vs FLUX.2 klein 4B, same references and prompt | Qwen 98 s (3 refs) / 135 s (5 refs); klein 21-24 s / 40 s. With 5 references klein **duplicated a person** and recoloured the extras; Qwen was right, so Qwen is the default. |
| shot stills, all 25 | Qwen-2.1 edit, `--verify` | 85-100 s with 2-3 references, 130-135 s with 5. **22 of 25 kept** on first review. Rejected: a two-extras shot where both extras got the cast member's face; a missing prop detail; a prop drawn too small. |
| voice, 11 lines | Qwen3-TTS 1.7B VoiceDesign (MLX) | 14 s for all lines. After the whisper-checked retries and fit-by-tempo (≤1.35x), every line matched the script at 0.83-1.0; one line was sped up 1.24x. |
| music bed | MiniMax-Music3 mxfp8 | 109 s. It returned 38.4 s of a requested 62 s; the asked key held, the tempo did not (~103 bpm of 136 asked). `music.sh` therefore keeps the longest of 3 seeds and loops it. |
| animatic | `reel animatic` (CPU) | under a minute |
| clips, 25 shots, 3-10 s each | LTX-2.5 image-to-video via vidgen | mean 111 s a clip (73 s for 3 s, 366 s for 10 s); 25 clips in ~47 min. **20 of 25 kept** on the first take. Two redone (one made from a rejected still; one where a bystander did the shouting); two fixed by moving the in-point (an intruder walking in; a late reaction). |
| first full cut | `reel cut --compare` (CPU) | 61.25 s, 25 shots |

**Redos and the final cut.**
- A "no faces visible" framing drew headless figures, so that still was replaced by a crop of the wide take (the
  skill now says to do this). Redone clips took 76-206 s each; all four were better than take 1.
- **An audio-length bug found by machine check:** after `-ss`, clip audio began at a negative timestamp and
  `atrim=duration` dropped 0.09 s on 11 of 25 shots, so the mix ended 1 s early and cut the last line. Fixed with a
  timestamp reset and sample-exact trims; whisper then heard every narrator line through to the end.
- Loudness -15.2 LUFS after loudnorm and sidechain ducking (it was -19.7).

**Overall.** About 3 h 15 min of GPU time from the first portrait to the first cut, plus ~25 min of redos. The
stills (Qwen-2.1 edit) held identity; the weakest link was LTX motion with several people in frame.

## pi as the agent (`docs/pi-smoke-test.md`)

**Passed in 84 s** on Qwen3.8 Flash Next, including the model load. pi loaded the skill, ran `status` and `gate`,
made a stills sheet, described all three stills accurately with its own vision, judged the shot against its
`still` text, recorded the pick as `"by": "agent"`, wrote its note and committed. It started no GPU stage.

## too-much, drive mode (`projects/too-much`, stills stage)

38 shots, 114.9 s, written from the author's own screenplay. pi (Qwen3.8 Flash Next, local) makes every pick with
no human input and no re-shoots. Measured from the stage logs, 2026-10-05 18:24-21:37:
- 8 cast portraits, 12 identity views (2 verifier retries), 3 set plates at 1408x2560 (~280 s each).
- Shot stills: text-to-image ~45 s; 3-reference edits 83-95 s without a retry; 5-reference edits 103-120 s. The
  verifier failed 20 of 41 shot edits, and each failure re-runs the edit, doubling that still's time.
- Review misses: in two shots Qwen put the same character in the frame twice. pi caught one (shot 6, picked the
  clean take), but in shot 21 both takes had a doubled princess and pi's review flagged only one of them.
