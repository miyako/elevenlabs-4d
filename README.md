# elevenlabs-4d

Notes, prompts, skills and scripts for **localizing a screen-recorded product demo with an AI voice-over and background music**, learned on the 4D v21 "AI Agentic Framework" demo (English recording → Japanese narration, ElevenLabs + Suno).

The repo keeps **global** guidance (applies to any language) apart from **language-specific** tips.

```
docs/global/   workflow, ElevenLabs, video shortening, music, QA        (any language)
docs/ja/       Japanese narration: wording, pronunciation, 4D brand      (language specific)
prompts/       voice-design prompt and Suno style prompts (copy/paste)
skills/        Claude Code skills (SKILL.md) that point at the docs
tools/         reference scripts used in the project (ffmpeg, Whisper, ElevenLabs, librosa)
```

To add another language, create `docs/<lang>/` and a `skills/<lang>-narration/` next to the Japanese ones; do not put language rules into `docs/global/`.

## Quick start for a new project

1. Read `docs/global/01-workflow.md`.
2. Copy `skills/*` into the project's `.claude/skills/` (or your user skills folder) so Claude Code finds them.
3. Set up the ElevenLabs key with `npx -y @elevenlabs/cli@latest onboard init` (stores `ELEVENLABS_API_KEY` in `.env`; never paste keys into chat or commit `.env`).
4. Scripts in `tools/` expect the layout `output/10min/` (see `tools/README.md`); adapt paths rather than rewriting the logic.

## Status

Reference material from one finished project; scripts are not a packaged tool. Everything here was verified on macOS (Apple Silicon) with ffmpeg 7+, Python 3.12, `mlx-whisper`, `elevenlabs`, `librosa`.
