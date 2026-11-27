#!/usr/bin/env python3
"""Voice Design: 04_elevenlabs_prompt.md の声の説明からプレビュー音声を3本作る。
  python3 tools/design_voice.py          → 10min/voice_previews/preview_N.mp3 と IDを表示
選んだら:  python3 tools/design_voice.py save <generated_voice_id> "名前"   → voice_id を表示"""
import sys, re, base64, pathlib
from _el import client, ROOT
c = client()
if len(sys.argv) > 1 and sys.argv[1] == "save":
    v = c.text_to_voice.create(voice_name=sys.argv[3], voice_description="Japanese narrator for a software product demo. Calm, warm, trustworthy; natural, conversational delivery.", generated_voice_id=sys.argv[2])
    print("voice_id:", v.voice_id); sys.exit()
md = (ROOT/"output"/"04_elevenlabs_prompt.md").read_text(encoding="utf-8")
desc = re.search(r"Voice Design に貼る説明文\)\n\n```text\n(.+?)\n```", md, re.S).group(1)
sample = (ROOT/"output"/"10min"/"tts_txt"/"S04.txt").read_text(encoding="utf-8").strip()
out = ROOT/"output"/"10min"/"voice_previews"; out.mkdir(exist_ok=True)
r = c.text_to_voice.design(voice_description=desc, text=sample)
for i, p in enumerate(r.previews, 1):
    (out/f"preview_{i}.mp3").write_bytes(base64.b64decode(p.audio_base_64))
    print(i, p.generated_voice_id)
