# Intake: shape the human's vision before anything is drawn (2026-10-05)

The human's requirement: in `checkpoints` and `hands-on` mode they want to be **asked**, and to approve, before
the pipeline commits to a direction. Approval of finished takes comes later; the intake is how they steer the start.
`drive` mode skips the questions (it fills every blank with defaults and says which it chose), but still writes
the beat sheet into the final report.

Keep it short: **one round of questions, then two approvals** (the brief, the look). Every question has a default,
so "defaults" or "you choose" is always a valid answer. Never ask about something the human already said.

## Round 1: the questions (one message; in Claude Code one AskUserQuestion call, at most four questions)

Ask only what is missing, in this order of importance:

1. **The story.** What happens, and how it ends (the punchline or final image)? Or give a reference video to learn the rhythm and look from.
   - A reference video goes to `reel-reverse` first; its craft notes (pacing, voice, music, look) answer most of the rest; the story stays original.
   - Default: offer three loglines built from whatever the human gave, and let them pick or edit.
2. **Length and language.** Options: 30 s (about 15 shots), 60 s (about 25-30), 90 s (about 40). Language for the
   voice: English, Russian or any Qwen3-TTS language.
   - Default: 60 s, English, 9:16.
3. **Voice and sound.** A narrator (what kind of voice)? Do characters speak, and which lines matter? What kind of
   music?
   - Default: a deep, slow storyteller narrator; short character lines only; a light score to match the tone.
4. **Who decides from here.** checkpoints (the default) or hands-on; or drive, if they want to hand it over now.
   Offer to change the gates.

Claude Code: one AskUserQuestion call with these as up to four questions, each with a recommended default first.
pi: a numbered list in plain text, each with its default in brackets, and "answer any you care about; I'll use
the defaults for the rest".

## Write the project, then approval 1: the brief

1. Write `projects/<p>/reel.toml` from the answers. Include:
   - the cast, each with ONE sentence and a voice;
   - the sets;
   - every shot (`dur`, `still`, `motion`, `audio`);
   - the narration;
   - the overlays;
   - **2-4 `[[look_option]]`s**: one safe, one bolder, one unexpected; each a full `image` style sentence plus a
     short `video` one.
2. `reel lint <p>` (exit 0), then `reel brief <p>`. Show the beat sheet: one line per shot with the time, length,
   framing, place, who, what we see and what is heard.
3. `reel gate <p> brief`. On a stop, ask:
   - Does the story land?
   - Is any beat missing, too long or out of order?
   - Is the ending right?
   Apply every change to `reel.toml`, re-run `reel brief`, and repeat until they say yes. Then run
   `reel approve <p> brief --by human`.

## Approval 2: the look (by eye, not by adjective)

1. `reel looktest <p>`: one test frame per look option, the lead in the main set, about a minute each on the GPU.
   Add `--clips` for a 2 s moving test.
2. `reel open <p> look` puts them side by side, left to right in id order. Say in one line what each one is.
3. `reel gate <p> look`. On a stop, the human picks (`reel pick <p> look <id> --by human`), mixes ("the light of
   warm with the palette of cold": write a new option and re-test it), or asks for new options. In drive mode,
   pick the one closest to the brief yourself and say why.
4. The picked option replaces `[look]` in every prompt from here on. No file edit is needed: `reel status` shows
   which look is active.

## Then the normal process

The cast portraits are the next checkpoint (by default): the human approves the faces before any shot is composed.
After that come the stills, the animatic and the cut (`SKILL.md`, "The process").
