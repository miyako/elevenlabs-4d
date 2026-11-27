#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_ja_draft.md の各シーンの `>` 行を読み、ElevenLabs 用に読みを付けた原稿
(04_elevenlabs_script.md)を作り直す。ドラフトを修正したあとに実行する。
  python3 tools/make_tts.py          # 14分版
  python3 tools/make_tts.py 10min    # 10分版
"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
READ = [  # 長い語から順に置換する。英語表記はそのまま渡し、4D と v21 だけ読みを指定する(試聴で確認済み)
 ("4D v21","ふぉおでぃい ぶいにじゅういち"),("v21","ぶいにじゅういち"),("4D","ふぉおでぃい"),("Gemma","じぇま"),
]
import sys
sub = sys.argv[1] if len(sys.argv)>1 else ""
base = root/sub if sub else root
src = (base/("03_ja_draft_10min.md" if sub=="10min" else "03_ja_draft.md")).read_text(encoding="utf-8")
out = ["# ElevenLabs 用ナレーション原稿(読み付き)","",
       "`tools/make_tts.py` で `03_ja_draft.md` から自動生成。シーンごとに1本ずつ生成し、ファイル名を `S01.mp3` のようにシーン番号で保存してください。","",
       "**ElevenLabs には、この .md ではなく `tts_txt/S01.txt` などのプレーンテキストを貼ってください**(この .md の見出し記号などは読み上げられます)。","",]
plain = []
for m in re.finditer(r"^## (S\d+) ｜ (.+?) ｜ (.+?)\n(.*?)(?=^## |\Z)", src, re.S|re.M):
    sid, tc, title, body = m.groups()
    q = re.search(r"^> (.+)$", body, re.M)
    if not q: continue
    t = q.group(1)
    for a,b in READ: t = t.replace(a,b)
    t = re.sub(r"(?<=[A-Za-z])_(?=[A-Za-z])", " ", t)   # メソッド名のアンダースコアは読まず、英語の語として読ませる
    plain.append((sid, t))
    out += [f"## {sid} ｜ {tc} ｜ {title}","","```text",t,"```",""]
(base/("04_elevenlabs_script_10min.md" if sub=="10min" else "04_elevenlabs_script.md")).write_text("\n".join(out), encoding="utf-8")
txt = base/"tts_txt"
txt.mkdir(exist_ok=True)
for f in txt.glob("*.txt"): f.unlink()
for sid, line in plain: (txt/f"{sid}.txt").write_text(line+"\n", encoding="utf-8")
print("wrote 04_elevenlabs_script.md")
