#!/usr/bin/env python3
"""「4Dの」だけ抑揚が変わる問題の切り分け。助詞つき/複合語/他の位置の「4D」を比べる。
  python3 tools/cadence_test2.py <voice_id>  → 10min/cadence_4D/round2/"""
import sys
from _el import client, ROOT
voice = sys.argv[1]; X = "ふぉおでぃい"
OPT = {
 "a": ("複合語にする", f"実際に動くのは、私が書いた{X}コードです。"),
 "b": ("現状(助詞「の」)", f"実際に動くのは、私が書いた{X}のコードです。"),
 "c": ("助詞を「で」に変える", f"実際に動くのは、{X}で書いたコードです。"),
 "d": ("読点で区切る", f"実際に動くのは、私が書いた、{X}のコードです。"),
 "e": ("S09の「4D自身」", f"仕事をしているのは、エルエルエムではなく、{X}自身なんです。"),
 "f": ("S03の「4D v21」", f"接続の管理は、{X} ぶいにじゅういちにおまかせ。"),
}
out = ROOT/"output"/"10min"/"cadence_4D"/"round2"; out.mkdir(parents=True, exist_ok=True)
c = client(); lines = []
for k, (memo, text) in OPT.items():
    lines.append(f"{k}: {memo}\n   {text}")
    for seed in (1, 2):
        with open(out/f"{k}_seed{seed}.mp3", "wb") as w:
            for ch in c.text_to_speech.convert(voice, text=text, model_id="eleven_v4", language_code="ja", seed=seed, output_format="mp3_44100_128"): w.write(ch)
(out/"options.txt").write_text("\n".join(lines)+"\n", encoding="utf-8"); print("done")
