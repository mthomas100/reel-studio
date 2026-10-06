---
name: reel-reverse
description: Study a reference AI reel or short video (a screen recording of Instagram/TikTok, or a downloaded file) as part of reel-studio's image-first reel pipeline (inspired by the still-first workflow AI short creators use - image model → image edit → image-to-video → music), turning it into craft notes - its pacing (shot-length range, where cuts land against the voice), shot sizes and camera behaviour, voice pacing and pitch, music tempo and key, the look - and then a reel-studio project file for an ORIGINAL reel that uses that craft. Use when the user shares a video and asks to break it down, analyse it, figure out how it was made, or "make something in this style"; then hand the project to reel-studio. Never a shot-for-shot copy.
---

# reel-reverse — from a reference video to a project you can build

Use it to learn how a reel works (its rhythm, its shot sizes, its voice and music, its look), then write your own
reel with that craft. The reference's frames, script and audio are someone else's work: study them, never publish
them, and never use them as inputs to your reel (see "Honesty rules").

## 1. Find the reel inside the file (CPU, minutes)

- `ffprobe` the file: length, size, fps, audio.
- A **phone screen recording** has app UI drawn over the picture: the status bar, a column of buttons on the right,
  a caption and a comment bar at the bottom. Crop away only what lies outside the picture (the comment bar); you
  cannot remove the overlay, so tell every reader to ignore it.
  Read the caption: it often names the story.
- **Loops.** A screen recording usually starts mid-reel and replays it. Run cut detection once on the whole
  recording, then look for two cut lists offset by a constant. That constant is the reel's length, and it fixes
  the true start. Cut the pieces out with `bin/reverse --start/--end` and join them in the reel's own order.

## 2. Measure it (CPU, about 3 minutes)

`bin/reverse <reel.mp4> <outdir> --lang <ru|en|auto>` (from the reel-studio repo) writes:
- dense frames at 6 fps;
- candidate cuts and shots;
- per-shot strips and key frames, plus sheets of four strips;
- Demucs stems;
- a whisper transcript;
- per-line voice pitch: about 85 Hz is a deep bass narrator, 400 Hz and up a shriek;
- the music's tempo and key.

## 3. Read the craft, not the content

The point is to learn *how* the reel works, so you can make something original with the same craft. Write
`analysis/craft-notes.md` (private, like the rest of the teardown):

1. **Read the sheets** (`shots/sheet-*.jpg`) once, to understand the structure: hook, escalation, turn, payoff,
   loop.
2. **Pacing.** From `shots.tsv`: shot count, median and range of shot lengths, how many shots are under 1 s, where
   the long holds sit. Check doubtful cuts with a full-resolution frame
   (`ffmpeg -ss T -i reel.mp4 -frames:v 1 ...`).
   - Common false cuts: whip pans, fast head turns, rack focus, a flash.
   - Common missed cuts: two similar wides back to back.
3. **Cuts against the voice.** From `transcript.srt` and `cuts.tsv`: how long after a line ends the cut lands, and
   whether long lines carry a montage. Note the numbers, not the words.
4. **Voices and music.** Narrator pitch range and pace from `voices.tsv`; the music's tempo and key from
   `music.json`; how loud the bed sits under the voice.
5. **Shot grammar.** The mix of shot sizes (close-up / medium / wide), how often the camera moves, title placement
   and timing. Counts and tendencies, not a description of each frame.
6. **Look.** Palette, light, lens feel, texture, in general terms, as raw material for your own `look.image`.
7. **Uncertain is fine.** Mark anything you could not measure; never guess silently.
8. **External research.** Look for public making-of posts and interviews about the format, and note the tools
   they name. Cite what you read; quote sparingly.

## 4. Write an original plan

- **Story.** Your own premise, game (what repeats and escalates), turn, punchline and loop. The reference's
  structure can inspire the shape; its plot, characters and jokes are not yours to reuse.
- **Look.** Your own style sentence for `look.image` and `[[look_option]]`s, informed by the craft notes.
- **Cast.** Your own characters: one fixed sentence each (an invented name, an age, three traits that survive a
  wide shot, the costume) and a voice line. Never copy a real person's likeness or the reference's characters.
- **Sets.** Your own locations, one empty-plate prompt each.
- **Shots.** Your own shot list. Use the reference's pacing (shot-length range, where cuts land) as a guide, never
  its shots one-for-one or descriptions of its frames.
- **Voice track.** Your own lines, paced like the reference (how soon a cut follows a line, how long the pauses
  are). `text_ru` (or another language) can sit alongside an English `text`.
- **Overlays.** Your own titles, placed and timed with the same care.

Then `reel lint`, and hand over to `reel-studio`.

## Honesty rules

- Describe what is measured; mark guesses as guesses.
- Never use a real person's face or the reference's frames as conditioning images. Build from text and your own
  generated references; the reference video is only for private comparison of pacing (`reel cut --compare`).
- The teardown (frames, stems, transcript, craft notes) stays private: it is someone else's work. Keep it out of
  any repo you publish.
