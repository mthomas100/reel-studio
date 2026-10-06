# Prompt craft for an image-first reel (tool-level notes, 2026-10-04)

What the stills, edits, clips and cut need in order to hold up, gathered from vendor prompting guides, community
write-ups and this rig's own runs. Tags: **[primary]** a model's own docs, **[community]** a practitioner guide or
thread, **[ours]** measured or decided on this rig. Links are under "Sources".

## 1. The order of work

The still-first workflow, as AI short creators describe it in public making-of posts:
1. Write the story as a shot list (a hook in the first 2 s, an escalating middle, a turn, a punchline, a loop).
2. Design the cast and the sets as hero stills.
3. Make every shot's first frame by **editing the hero stills** (the same references into every shot).
4. Check the pacing with the stills held to the voice track (an animatic) before spending GPU time on video.
5. Animate each still for a few seconds; use 0.2-3 s of it.
6. Lay narration, music and titles over a fast cut; grade everything once at the end.

reel-studio is that order as commands: `reel cast/sets` → `reel views` → `reel stills` → `reel voice/music` →
`reel animatic` → `reel animate` → `reel cut`.

## 2. Hero stills (text-to-image, Qwen-Image-2.1)

- **Identity first, scene second, texture last.** Open with who (2-3 hyper-specific physical details), then the
  scene, then a closing texture line ("natural skin texture, natural proportions"). Scene-first prompts give a
  generic face. [community]
- **Prose, not tags.** Qwen-Image follows flowing prose of about 200 words; keep the whole prompt in one language
  (a single Chinese character routes it through its Chinese prompt rewriter). [community, primary]
- **Describe positively.** "An empty marble floor" works better than "no people". Google calls these semantic
  negative prompts; FLUX.2 has no negative prompt at all. [primary]
- **Size.** Width and height multiples of 16 for text-to-image, 32 for the edit command; 704x1280 (9:16) works with
  both and with LTX-2.5. [primary, ours]
- **Avoid freckle-heavy faces** for a recurring character: they never come out the same twice. [community]
- **Sets are empty plates.** One per location, no people, rendered at twice the reel's size so edits can crop.
  [ours]
- **Pseudo-text.** Qwen paints letters on signs even when told not to. Titles go in the cut (`[[overlay]]`), never
  in a prompt. [ours]

## 3. The same people in every shot (multi-reference edit, Qwen-Image-2.1 edit)

- **Name each reference by position.** "Picture 1: the place. Picture 2: Zlata. Picture 3: a close-up of Zlata's
  face." Qwen-Image-Edit was trained on this "Picture N:" form; keep the descriptions simple. `bin/reel` writes
  every edit prompt this way (`still_prompt`). [community]
- **Say how the pieces relate, then list what stays:** "Zlata from Picture 2 sits on the throne in Picture 1. Keep
  the architecture and light of Picture 1; Zlata keeps exactly the face, hair, headdress and costume of Picture 2."
  [primary: BFL multi-reference guide]
- **Base image first** (it sets the aspect ratio), name subjects directly instead of using pronouns, and choose
  verbs that limit the change ("change the clothes", not "transform"). [primary: BFL]
- **An identity sheet beats a single portrait.** `reel views` draws a face close-up, a three-quarter and a profile
  view from the picked portrait; the face close-up goes into every shot as a second reference. [ours]
- **Edit from the references, never from the previous shot.** Chained edits drift and inherit blur and grain. [primary:
  Google; community]
- **Extras are not cast.** Using one cast portrait for "two maids" gives both maids the same face. Describe extras
  in the still text with distinct hair or age. [ours]
- **Partial framings are crops.** "Cut off at the chest so no faces are visible" drew headless figures. Draw the
  wide still and crop it. [ours]
- **Five references usually hold,** but Qwen still doubles a person now and then (too-much shots 6 and 21, where a
  second Tsarina or a second Zlata appeared in the background). Check both edges of every frame. [ours]
- **Verify, then look.** `--verify` asks Qwen3-VL whether the edit applied and retries once. It often fails a good
  edit on "outside_unchanged" (a re-composed shot is supposed to change the frame), which doubles that still's time,
  and it did not catch the doubled-person failures; the contact-sheet review has to. [ours]

## 4. Image-to-video (LTX-2.5 via vidgen)

- **Image-to-video grows the shot out of the frame you give it,** so half the prompt protects what is there: say
  which objects stay still, keep the camera locked when the composition matters, one event per clip. [primary-ish:
  fal LTX-2.5 guide]
- **One action and one camera move, in one or two sentences.** More motion means more face drift. [community]
- **Put the peak in the still.** Generate the still already mid-expression (the pout, the laugh) and animate the
  continuation; morphing from calm to a wail is where faces break. [ours]
- **Name who speaks and close every other mouth,** or a bystander does the shouting. [ours]
- **Describe facial mechanics, not emotion words** ("lips trembling", "eyes narrowing"). [community]
- **"Real" for animals and giant props** ("a real white pony"), or they drift to CGI. [ours]
- **No lens or format words** ("35mm", "film grain", "anamorphic"): on LTX they draw borders and masks. [ours]
- **"Cut to" inside a clip makes a real cut.** One take per shot; split beats into shots. `reel lint` flags both.
  [ours]
- **Generate 3-4 s, use 0.2-3 s.** The first frames sit pinned to the still, so the default in-point is 0.4 s.
  LTX may walk a stranger into a wide late in the take; cutting before it is cheaper than a redo. [ours]
- **Re-anchor every shot on its own still,** never on the last frame of the previous clip (that compounds
  sharpening and exposure drift). [community]

## 5. Voice and music

- **Voice design from a persona sentence:** age, timbre, pitch, pace, accent, attitude ("a man of about sixty
  with a dry crisp British RP voice, perfectly deadpan"). One voice per character, set on the `[[cast]]` entry.
  [ours, Qwen3-TTS VoiceDesign]
- **Machine-check every line.** `scripts/voice.py` transcribes each take with whisper and re-speaks it with a new
  seed when the words come out wrong (up to 3 tries), then speeds a line up by at most 1.35x if it would run into
  the next one. [ours]
- **Music duration is an upper bound.** MiniMax-Music3 returned 38 s of a requested 62 s; tempo and key in the
  caption are probabilistic. `scripts/music.sh` keeps the longest of 3 seeds and loops it with crossfades. [primary:
  mlx-audio README; ours]

## 6. The cut

- **Cut on the narration:** one line per shot (or a 3-5 shot montage under a long line), cutting 0.3-0.5 s after
  the line ends. One-word shouts get their own short shot. [ours]
- **Hook in the first 2 seconds:** a striking face, a title line, a voice. [community]
- **Titles:** white, centred, a typewriter reveal is optional (`typewriter = <seconds>`); keep them clear of the
  bottom ~20 % and right ~15 % of a 9:16 frame, where the app's UI sits. [ours]
- **Duck under the narrator.** The cut sidechain-compresses the takes' own sound and the music whenever the narrator
  speaks, then normalises to -14 LUFS (the common target for social video; not confirmed for any one platform).
  [ours, community]
- **Grade once, globally.** One colour pass and one grain pass over the whole reel hides small colour differences
  between generations. [ours]
- **The loop:** make the last shot repeat the first shot's set-up, with the expression or prop changed, so the
  restart reads as intended. [community]

## Sources (read 2026-10-04)

- Black Forest Labs: multi-reference editing https://docs.bfl.ml/guides/prompting_editing_multi_reference.md ;
  single-reference editing https://docs.bfl.ml/guides/prompting_editing_single_reference.md ; FLUX.2 editing
  https://docs.bfl.ml/flux_2/flux2_image_editing.md
- Google: Gemini image prompting
  https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/ ;
  Veo 3.1 prompting https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Qwen-Image model card https://huggingface.co/Qwen/Qwen-Image ; Qwen-Image-Edit-2511
  https://huggingface.co/Qwen/Qwen-Image-Edit-2511
- fal.ai, "How to use LTX-2.5" (2026-08-16) https://fal.ai/learn/tools/how-to-use-ltx-2-5 ; "How to use Kling 3.0
  Pro" (2026-06-14) https://fal.ai/learn/tools/how-to-use-kling-3-0-pro
- Runway, Seedance 2.0 prompt guide https://runway.com/resources/seedance-2-0-prompt-guide
- Community: the "Picture N:" convention for Qwen Edit (an r/StableDiffusion guide to Qwen Edit 2511, 2026);
  continuity tips (r/VEO3, 2025)
  https://old.reddit.com/r/VEO3/comments/1okwgqa/ ; identity and motion threads on r/KlingAI_Videos and
  r/GenAIGallery (2026)
- CapCut, seamless loops https://www.capcut.com/create/seamless-loop-videos-continuity-techniques
- mlx-audio (MiniMax-Music3, Qwen3-TTS) https://github.com/Blaizzy/mlx-audio
