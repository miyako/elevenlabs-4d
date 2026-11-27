#!/usr/bin/env python3
"""tts_txt/*.txt を ElevenLabs で音声にして narration/ に保存する。
  python3 tools/make_narration.py <voice_id> [S04 S05 ...]   # シーン指定なしなら全シーン
声の設定は試聴時と同じ(ボイスの既定値)。モデル既定は eleven_v4(language_code=ja)。前後のシーンの文を渡して、つなぎ目が自然になるようにする。"""
import sys, os, subprocess, numpy as np
from _el import client, ROOT
voice, only = sys.argv[1], sys.argv[2:]
model = os.environ.get("EL_MODEL", "eleven_v4")
d = ROOT/"output"/"10min"; files = sorted((d/"tts_txt").glob("S*.txt"))
texts = [f.read_text(encoding="utf-8").strip() for f in files]
out = d/"narration"; out.mkdir(exist_ok=True)
c = client()
FF = os.environ.get("FFMPEG", "ffmpeg")
def onset_db(path):
    """冒頭20ミリ秒の最大ピーク(dB)。-38dB より大きいと、語頭が途中から始まっている(語頭が欠けている)。"""
    raw = subprocess.run([FF, "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "44100", "-t", "0.05", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(float)/32768
    return 20*np.log10(abs(a[:882]).max()+1e-9)
SKIP_CHECK = os.environ.get("EL_NOONSETCHECK", "").split(",")
for i, f in enumerate(files):
    if only and f.stem not in only: continue
    lead = "" if f.stem in os.environ.get("EL_NOLEAD", "S03").split(",") else "……"   # 先頭に「……」を付けると、語頭が欠けずに自然に立ち上がる
    kw = dict(text=lead+texts[i], voice_id=voice, model_id=model, language_code="ja",
              output_format="mp3_44100_128")
    nocontext = f.stem in os.environ.get("EL_NOCTX", "S03").split(",")   # S03 は前後の文を渡さない方が「4D v21」の抑揚が合う
    if i > 0 and not nocontext: kw["previous_text"] = texts[i-1]
    if i < len(files)-1 and not nocontext: kw["next_text"] = texts[i+1]
    best = None
    for attempt in range(7):                      # 語頭が欠けたクリップは、シードを変えて取り直す
        if attempt: kw["seed"] = 100+attempt
        tmp = out/f"{f.stem}.try.mp3"
        with open(tmp, "wb") as w:
            for ch in c.text_to_speech.convert(**kw): w.write(ch)
        ob = onset_db(tmp)
        if best is None or ob < best[0]:
            best = (ob, tmp.read_bytes())
        if ob <= -38 or f.stem in SKIP_CHECK: break
    tmp.unlink()
    (out/f"{f.stem}.mp3").write_bytes(best[1])
    print("wrote", out/f"{f.stem}.mp3", f"(語頭 {best[0]:.0f}dB, 試行 {attempt+1}回)")
