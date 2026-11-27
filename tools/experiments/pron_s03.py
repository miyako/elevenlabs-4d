#!/usr/bin/env python3
"""S03 の「4D v21」の抑揚を、言い回し・読み・前後の文脈の有無を変えて比べる。
  python3 tools/pron_s03.py <voice_id>  → 10min/pron_s03/"""
import sys
from _el import client, ROOT
voice = sys.argv[1]; d = ROOT/"output"/"10min"; out = d/"pron_s03"; out.mkdir(exist_ok=True)
D = "ふぉおでぃい"
rest = "私は手元のローカルモデルなので、APIキーも要りません。もちろん、OpenAIやClaudeを選んで、キーを入れることもできますよ。"
V = {
 "A": f"もう一つ、{D} ぶいにじゅういちで新しく加わった「AI」の設定です。使うAIプロバイダーを登録するだけで、接続の管理は、{D} ぶいにじゅういちにおまかせ。{rest}",
 "B": f"もう一つ、{D} ぶいにじゅういちで新しく加わった「AI」の設定です。使うAIプロバイダーを登録するだけで、接続の管理は、すべておまかせ。{rest}",
 "C": f"もう一つ、{D} ゔぃいにじゅういちで新しく加わった「AI」の設定です。使うAIプロバイダーを登録するだけで、接続の管理は、すべておまかせ。{rest}",
 "D": f"もう一つ、{D} ゔぁあじょん にじゅういちで新しく加わった「AI」の設定です。使うAIプロバイダーを登録するだけで、接続の管理は、すべておまかせ。{rest}",
}
prev = (d/"tts_txt"/"S02.txt").read_text(encoding="utf-8").strip(); nxt = (d/"tts_txt"/"S04.txt").read_text(encoding="utf-8").strip()
c = client(); lines = []
for k, text in V.items():
    lines.append(f"{k}: {text}")
    for tag, kw in (("ctx", dict(previous_text=prev, next_text=nxt)), ("solo", {})):
        with open(out/f"{k}_{tag}.mp3", "wb") as w:
            for ch in c.text_to_speech.convert(voice, text=text, model_id="eleven_v4", language_code="ja", output_format="mp3_44100_128", **kw): w.write(ch)
(out/"options.txt").write_text("\n".join(lines)+"\n", encoding="utf-8"); print("8 clips")
