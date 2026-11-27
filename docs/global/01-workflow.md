# Workflow: localizing a screen-recorded demo

The goal is a new voice-over and music for a screen recording, **not a transcript read aloud**. Spoken demos are rambling; write a fresh, lively script that follows the same screen and the same facts.

## Steps

1. **Transcribe** the audio with timestamps (Whisper large-v3-turbo; on Apple Silicon `mlx-whisper`). Keep the raw SRT. Clean it by hand against what is on screen; mark unclear audio `[?]`.
2. **Timesheet**: split the recording into scenes (topic changes), with start/end, what is on screen, and a one-line gist. Take timings from the transcript, not from thumbnails (see the warning below).
3. **Draft the target-language script** per scene. Facts, numbers and order stay; wording is free. Give each scene a character budget from its duration (see `docs/ja/` for the Japanese rate).
4. **Review loop**: the user edits the draft; everything downstream is regenerated from the draft (single source of truth).
5. **Voice**: design a voice (`docs/global/02-elevenlabs.md`), generate one clip per scene, QA the clips (`05-qa.md`).
6. **Shorten the video** to fit the narration (`03-video-editing.md`): trim only still frames, retime only moving frames.
7. **Music** (`04-music-bgm.md`): a few Suno tracks, joined on bar lines, constant low level, natural ending.
8. **Mux** narration (+music) with the edited video, then check joins and spot-check by timestamp.

## Rules that saved time

- Show the user A/B/C test clips for anything about sound (pronunciation, cadence); let them pick by letter. Name files so the choice is unambiguous (`Vb2.mp3`) and keep a `options.txt` with the exact text.
- When the user reports a timestamp, map it to a scene through `edl.json` before guessing. Their times refer to the video they last watched; scene starts shift whenever narration length changes.
- Keep every generated artifact reproducible from the draft by script; do not hand-edit audio.
- Tell the user what you did **not** verify (you cannot listen). Say "I haven't listened" instead of implying it sounds right.

## Pitfall: contact-sheet timestamps

Thumbnails made with `ffmpeg -vf fps=1/20` were off by up to ~15 s from the true frame times in this project. Use `select=eq(n,N)` or `trim` for exact frames, or match against frames extracted with `-ss`.

## Pitfall: ffmpeg availability

No Homebrew ffmpeg was installed. `pip install imageio-ffmpeg` provides a binary; symlink it as `ffmpeg` and put it on `PATH` for libraries (mlx-whisper shells out to `ffmpeg`).
