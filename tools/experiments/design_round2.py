#!/usr/bin/env python3
"""2回目: 前回のプレビュー3を新しい読みで聞き直し(声をアカウントに保存して再生成)、新しい声を2つ作る。"""
import re, base64
from _el import client, ROOT
c = client()
md = (ROOT/"output"/"04_elevenlabs_prompt.md").read_text(encoding="utf-8")
desc = re.search(r"Voice Design に貼る説明文\)\n\n```text\n(.+?)\n```", md, re.S).group(1)
sample = (ROOT/"output"/"10min"/"tts_txt"/"S04.txt").read_text(encoding="utf-8").strip()
out = ROOT/"output"/"10min"/"voice_previews"
# A: 前回のプレビュー3
try:
    v = c.text_to_voice.create(voice_name="JA narrator (kept preview 3)", voice_description=desc[:400], generated_voice_id="q1snISISEjadaVxqiOyI")
    with open(out/"r2_A_kept_preview3.mp3","wb") as w:
        for ch in c.text_to_speech.convert(v.voice_id, text=sample, model_id="eleven_v4", language_code="ja", output_format="mp3_44100_128"): w.write(ch)
    print("A saved voice_id:", v.voice_id)
except Exception as e:
    print("A failed:", repr(e)[:300])
# B, C: 新しい声
r = c.text_to_voice.design(voice_description=desc, text=sample)
for name, p in zip("BC", r.previews[:2]):
    (out/f"r2_{name}_new.mp3").write_bytes(base64.b64decode(p.audio_base_64))
    print(name, p.generated_voice_id)
