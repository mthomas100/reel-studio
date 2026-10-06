# pi smoke test (run with the GPU free: pi's own model has to load)

    bin/reel-pi -p "$(cat docs/pi-smoke-test.md | sed -n '/^PROMPT/,$p' | tail -n +2)"

Pass: pi loads the skill, runs status and gate, makes a sheet, reads it with its own vision, gives a reasoned
choice, records it with `bin/reel pick` (picks.json shows "by": "agent" for still 12), and starts no GPU stage.
It needs a project whose stills 11-13 exist; the prompt below uses `too-much`. (The recorded pass, 2026-10-05 01:04,
ran on the private test project; see docs/test-runs.md.)

PROMPT
Load the reel-studio skill. Project: too-much. Do NOT run any GPU stage (no cast, views, sets, stills, animate,
voice or music). 1) Run `bin/reel status too-much` and tell me the control mode. 2) Run
`bin/reel gate too-much stills` and say whether you must stop for the human. 3) Run
`bin/reel sheet too-much stills --shots 11-13 --cols 3` and open the printed image with the read tool. 4) Describe
what you see in each of the three stills in one line each, and judge whether shot 12 matches its `still` text in
projects/too-much/reel.toml. 5) Record your choice with `bin/reel pick too-much still 12 1`. 6) Append one line
to projects/too-much/NOTES.md saying what you checked and decided, starting with "pi:".
