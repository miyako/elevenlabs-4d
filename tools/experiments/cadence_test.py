#!/usr/bin/env python3
"""「4D」の読み方(抑揚)の候補を、同じ文で複数作って聞き比べる。
  python3 tools/cadence_test.py <voice_id>  → 10min/cadence_4D/ に 候補×シード2種 を保存"""
import sys
from _el import client, ROOT
voice = sys.argv[1]
SENT = "こちらは、従来型の{X}アプリです。実際に動くのは、私が書いた{X}のコードです。"
OPT = {  # 記号: 狙い(平板型 低→高→高→高)
 "A": ("ふぉおでぃい", "現在の表記"),
 "B": ("フォーディー", "カタカナ(長音符)"),
 "C": ("4D", "そのまま英数字"),
 "D": ("ふぉーでぃー", "ひらがな+長音符"),
 "E": ("、ふぉおでぃい", "直前に読点を置いて語頭を上げ直す"),
 "F": ("ふぉおでぃぃ", "語尾を小さい「ぃ」にして語尾を落とさない"),
 "G": ("ふぉ おでぃい", "「ふぉ」と「おでぃい」の間に空白(上昇を作る)"),
}
out = ROOT/"output"/"10min"/"cadence_4D"; out.mkdir(exist_ok=True)
c = client(); lines = []
for k, (x, memo) in OPT.items():
    text = SENT.replace("{X}", x)
    lines.append(f"{k}: {memo}\n   {text}")
    for seed in (1, 2):
        with open(out/f"{k}_seed{seed}.mp3", "wb") as w:
            for ch in c.text_to_speech.convert(voice, text=text, model_id="eleven_v4", language_code="ja", seed=seed, output_format="mp3_44100_128"): w.write(ch)
        print("wrote", f"{k}_seed{seed}.mp3")
(out/"options.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
