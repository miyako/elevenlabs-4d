---
name: localize-screen-demo
description: Localize a screen-recorded product demo with an AI voice-over (ElevenLabs) and background music (Suno): transcribe, timesheet, rewrite the script, generate and QA narration, shorten the video by trimming still frames only, and mix. Use when asked to produce a dubbed or voice-over version of a demo video, or to fix narration/music/edit problems in one.
---

# Localize a screen-recorded demo

Read these files from the `elevenlabs-4d` repository (or its copy in the project) before acting:

1. `docs/global/01-workflow.md` for the end-to-end order and the working rules.
2. `docs/global/02-elevenlabs.md` before calling ElevenLabs (plain text only, model limits, clipped-onset fix).
3. `docs/global/03-video-editing.md` before touching the video (trim/hold still frames only; no pointer edits).
4. `docs/global/04-music-bgm.md` for Suno prompts and bar-aligned joins.
5. `docs/global/05-qa.md` before sending anything; run the checks and report what was not verified.
6. The language folder `docs/<lang>/` for pronunciation and wording rules of the target language (Japanese: `docs/ja/narration-ja.md`, skill `ja-narration`).

Key behaviours:

- The script is a re-telling, not a translation; the draft file is the single source and everything downstream is regenerated from it.
- Never ask for, print or commit the API key; use `npx -y @elevenlabs/cli@latest onboard init` and `.env`.
- Offer letter-coded A/B sound tests and let the user choose; map reported timestamps to scenes via `edl.json`.
- You cannot listen: say what was measured and what was not.
- Reference scripts live in `tools/` (see `tools/README.md`).
