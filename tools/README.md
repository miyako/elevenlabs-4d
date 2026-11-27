# tools

Reference scripts from the 4D demo project. They assume this layout (relative to the project root):

```
video/<source>.mp4                    the screen recording
output/10min/draft script             03_ja_draft_10min.md  (`## S01 ｜ 00:00–… ｜ title` then a `> narration` line)
output/10min/tts_txt/S01.txt …        plain-text narration per scene (made by make_tts.py)
output/10min/narration/S01.mp3 …      ElevenLabs clips
output/10min/bgm/A.m4a B.m4a C.m4a   Suno tracks
output/10min/edl.json                 scene list; edit_video.py rewrites it
```

Order: `make_tts.py` → `make_narration.py <voice_id>` → `trim_narration.py` → `qa_narration.py` → `motion.py` → `edit_video.py` → `plan_bgm.py` → `make_10min_video.py`. Every script that needs ffmpeg takes its path as the first argument (a pip-installable binary: `imageio-ffmpeg`).

`build_edl.py` is the older bootstrap that created the first `edl.json`; `edit_video.py` needs an `edl.json` with scene ids and nominal `src_a` times. `experiments/` holds the A/B pronunciation test generators; copy and adapt them.

Python packages: see `requirements.txt` plus `numpy`, `librosa`, `mlx-whisper` (Apple Silicon) and `imageio-ffmpeg`.
