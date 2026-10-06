---
name: reel-studio
description: Make a short, fast-cut AI reel on this Mac with an image-first reel pipeline, inspired by the still-first workflow AI short creators use (image model → image edit → image-to-video → music) and rebuilt with local models: design hero stills of the cast and sets, edit them into a consistent still for every shot, animate each still for a few seconds with LTX-2.5, add a narrator and a music bed, and cut it all to a 30-90 s 9:16 reel with burned-in titles. Use when the user asks for a reel, an Instagram/TikTok-style AI short, an AI fairy tale, an image-first or still-first video, a reel in the style of a reference video, or names reel-studio. NOT the film rig's studio/film skills (one long text-first LTX take per shot, local-video); use those for multi-minute films with on-camera dialogue.
---

# reel-studio — the image-first reel pipeline

Home: this repo, reel-studio (its README says why it exists and how it differs from the film rig). One command does
every step: `bin/reel <command> <project>`, run from the repo root. The project is one text file,
`projects/<project>/reel.toml`; media goes to `~/Videos/reel-studio/<project>/`. Model choices live in
`config.toml`, never in a prompt or a skill.

This is a different machine from the film rig (`studio`, `film`, `scene-breakdown`, `screenplay` in
local-video). It shares two parts: `vidgen` (LTX-2.5 image-to-video) and the Mac's GPU hold. It shares no
project files.

| | the film rig (local-video) | reel-studio |
|---|---|---|
| unit | one text prompt → one 5-15 s take | one designed still → a 2-4 s clip, cut to 0.5-4 s |
| consistency | the cast sentence repeated, `[still]` | the SAME reference images (cast portrait + set plate) edited into every shot |
| dialogue | spoken on camera by LTX, sync-gated | a voice track (narrator + short lines) laid over the cut |
| length | 1-7 min | 20-90 s, about 25-40 shots |

## Who decides: the control dial (read this first)

The human sometimes wants to make every choice, and sometimes wants to hand the whole reel over. Both are
first-class, and they can switch mid-reel. The mode lives in the project file as `[control] mode`:

| mode | the agent | the human |
|---|---|---|
| `drive` | makes every pick, writes, renders and cuts to the end; then opens the cut and reports each choice with its reason | watches, and can change any choice afterwards |
| `checkpoints` (the default) | asks the intake questions; then drives, but stops at the gates (brief, look, cast, stills, animatic, cut by default; `gates = [...]` changes them): opens the sheet, proposes its picks in two to four lines, and waits | says "go", picks differently, or rewrites a shot |
| `hands-on` | stops after every stage; prepares 2-4 takes and options, carries out what the human chooses, and suggests prompt fixes | picks every take and approves every step |

The rules, in every mode:
1. **Ask once if the mode is unknown.** When the project has no `[control]` and the human hasn't said, ask one
   question: drive, checkpoints or hands-on. "Just make it" means drive. "Let me see the stills" means
   checkpoints with stills as a gate. Write the answer into the project.
2. **At the end of every stage, run `reel gate <p> <stage>`.**
   - Exit 3 means stop: run `reel open <p> <stage>` to put the result on the human's screen, propose your picks,
     and wait.
   - Exit 0 means go: review the sheet yourself, pick with `reel pick ...` (from an agent's shell it is recorded as an agent pick), write one line in
     `projects/<p>/NOTES.md` saying why, and carry on.
3. **The human's choices win.**
   - When you relay the human's pick, use `reel pick ... --by human`. The CLI never lets an agent overwrite a human
     pick.
   - A human's edit to `reel.toml` is never reverted. If you think it hurts the reel, say so once and keep it.
4. **The human can step in any time, in any mode.** "Let me pick the stills", "redo shot 7, she should be
   laughing", "just finish it" or "switch to hands-on" each take effect at once:
   - change the mode in the file when they switch;
   - rerun only what changed (`--shots`, `--only`, `--force`);
   - re-cut, which is cheap.
5. **Every decision is visible and reversible.**
   - Takes are numbered and kept; `picks.json` says who chose each one and when.
   - `reel status` shows the mode and every pick.
   - In drive mode the final report lists what you chose, so the human can overturn any of it with one pick and a
     re-cut.

## The process (follow it in order; each step has a check)

0. **Intake: ask, then get the brief and the look approved** (`references/intake.md`; skipped in drive mode).
   - One round of questions, each with a default: the story and ending (or a reference video), length and language,
     voice and sound, and who decides from here.
   - Then the beat sheet (`reel brief`) for the human to approve (`reel approve <p> brief --by human`).
   - Then 2-4 look options rendered as test frames (`reel looktest`, `reel open <p> look`) for them to pick by eye.
   - Nothing else is drawn until the brief is approved.
1. **Write the project** (`projects/<p>/reel.toml`; template `docs/reel-template.toml`, a full example
   `projects/too-much/reel.toml`). When the human gives a reference video, run `reel-reverse` first: it gives
   craft notes (pacing, cut timing, voice and music, look) for an original reel, never a shot list to copy. (In the intake this happens between the questions and the brief.)
   - The story fits the reel shape: a hook in the first 2 s (a striking face plus a title line), a world, three
     escalating attempts, a turn, a punchline image, and a last shot that loops back into the first.
   - Every recurring person is a `[[cast]]` with ONE fixed sentence (name, age, three fixed traits, costume). Every
     location is a `[[set]]`: an empty plate.
   - Every shot has `dur` (seconds in the cut), `still` (the first frame as an image prompt: framing, who, pose,
     expression, props, light) and `motion` (what moves in 2-4 s, and the camera).
   - The voice track is `[[narration]]` lines at reel times (narrator plus character lines with their own `voice`).
     The burned-in text is `[[overlay]]`.
   - Check: `reel lint <p>` (exit 0).
2. **Cast and sets.** Run `reel cast <p> --takes 2` and `reel sets <p>`, then `reel sheet <p> cast` and
   `reel sheet <p> sets`. LOOK at the sheets (Read the image), then follow the dial (`reel gate <p> cast`) before picking.
   - A reference portrait must show the whole costume and a clear face. Redo a take with odd hands, a wrong
     costume, text, or a second person.
3. **Stills** (the multi-reference edit step). Run `reel stills <p> --takes 2`, then `reel sheet <p> stills`. Review every
   shot against its `still` text:
   - the right person (face, hair, crown, costume as in the reference);
   - the right framing and expression;
   - no extra people, no garbled text, hands correct;
   - the set's look carried over.
   Pick with `reel pick <p> still <n> <take>`. A shot that fails twice gets its `still` text rewritten (more
   concrete, the framing first, one action), never just a new seed.
4. **Voice first, then the animatic.**
   - `reel voice <p>` (Qwen3-TTS VoiceDesign; `language` is english or russian among others) prints each line's
     start and end. Fix any line that overlaps the next by moving its `start` or shortening it.
   - `reel music <p>` writes the bed: the model is set in config.toml `[music]`, or set the project's
     `[music] file = ...`.
   - `reel animatic <p>` holds each picked still for its shot's length, with the voice, music and titles (CPU only).
     Watch it as frames. Fix pacing and any `dur` now, before video costs GPU time.
5. **Animate.** `reel animate <p>` makes a 3-4 s LTX-2.5 clip per shot, image-to-video through vidgen. Then
   `reel sheet <p> clips`. Reject:
   - morphing faces or melting hands;
   - a camera that drifts off the subject;
   - new people appearing.
   Redo with `--force --shots <n>` and a simpler `motion` (one action, one camera move). Acting shots often need 3-4
   takes (`--takes 3`); pick with `reel pick <p> clip <n> <take>`.
6. **Cut.** `reel cut <p> --compare`. The `--compare` file puts the reference on the left when the project has a
   `reference`. Watch `cut/<p>.mp4` as frames: `ffmpeg -i <cut> -vf fps=2,scale=180:-2,tile=8x8 sheet.jpg`, then
   Read it. Check:
   - the hook in the first 2 s;
   - every narration line lands on its shot;
   - the punchline reads;
   - the loop: the last shot flows into the first.

`reel status <p>` shows what exists and what is picked. `reel run <p> --from <stage>` runs the rest without
review: use it only for a second pass after the picks are made.

## Prompt craft (what makes the stills and clips hold up)

`docs/craft.md` holds the tool-level rules and their sources. In short:
- **Stills:** framing first ("Medium close-up, eye level, symmetrical:"), then who (the cast's first name: the
  reference image carries the look), the pose and the expression in physical terms ("chin down, glaring up
  through her fringe, lower lip pushed out"), props and their scale **in people** ("a cupcake taller than the maids
  wheeling it"), and the light of the set. The project's `look.image` is appended to every still, so never repeat
  the style.
- **Motion:** one action and one camera move, in 1-2 sentences: "She whips her head away. The camera holds."
  Expressive acting reads (crying, shrieking, a grin spreading). Fast, complex choreography does not.
- **Never prompt text.** Titles are `[[overlay]]`, drawn in the cut.
- **No lens or format words** ("35mm", "film grain", "anamorphic"): on LTX they draw borders and masks
  (local-video's `skills/film/references/prompt-rules.md`).
- **"Real" for animals and giant props** ("a real white peacock"): they drift to CGI without it.
- **Lessons from the first test reel (2026-10-04/05):**
  - **A tight or partial framing is a crop, not a prompt.** "The frame cut off at the chests so no faces are
    visible" drew headless maids. Draw the wide still, then crop it to 9:16 and save it as a new take.
  - **One recurring person per extra.** A cast reference used for "two maids" gave both her face. Leave extras out
    of `cast`.
  - **Name who shouts and close everyone else's mouth** in `motion`, or a bystander does the shouting.
  - **LTX may walk a stranger into a wide** late in the take. Cut before it with a smaller `in`/`dur`, which is
    cheaper than a redo.
  - **Five references are fine for Qwen-2.1 edit** most of the time (a three-person tableau held). FLUX.2 klein
    duplicated a person at five. Qwen still doubles someone now and then (too-much shots 6 and 21): check both edges
    of the frame.

## Discipline

- **The GPU hold.** Every GPU stage takes it by itself (`hold run`), queues behind other renders, and unloads the
  local LLM only while it runs. Never start a model server, never kill one, and never run two `reel` GPU stages at
  once.
- **Review by looking.** Judge stills and clips from the contact sheets: Read the image. As pi on a vision model, use
  the read tool on the sheet. Never ask the human to label or rate takes.
- **Keep everything.** Takes are numbered. A redo adds a take, or uses `--force` on one shot only. Write what failed
  and why in `projects/<p>/NOTES.md`.
- **Commit the project file and picks** in this repo (`reel-studio: <project>: <what>`). Media stays
  out of git.
