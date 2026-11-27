#!/usr/bin/env python3
"""発音テスト3: (1) 英語表記のまま渡す文 (2) 「4D v21」「v21」の読み方の候補。
  python3 tools/pron_test3.py <voice_id>  → 10min/pron3/ に保存、options.txt に本文"""
import sys
from _el import client, ROOT
voice = sys.argv[1]; out = ROOT/"output"/"10min"/"pron3"; out.mkdir(parents=True, exist_ok=True)
D = "ふぉおでぃい"
EN = {
 "E1": "画面には、フレームワーク付属の「Ask Me Anything」ボタンを一つ置きました。",
 "E2": "データベースは、LLMに送っていません。LLMが受け取るのは、使えるメソッドの一覧だけ。",
 "E3": "OpenAIやClaudeを選んで、APIキーを入力することもできます。",
 "E4": "MCPは、メソッドを呼び出すためのAPIのようなものです。",
 "E5": "「who am I?」。……「あなたはEvent Pulseマネージャーです」。トレースを見ると、AIが少し考えて、get_current_user を実行すると決めたのが分かります。",
 "E6": "weatherAdvisorには、weather_compare_weather、weather_fetch_for_event、weather_rationalize_weather を割り当てています。",
 "E7": "私は「auto」にして、Gemmaに向けています。財務向けの部分だけOpenAIにして、ほかはローカルのモデルにすれば、コストも抑えられます。",
}
V = {"a": "ぶいにじゅういち", "b": "ゔぃいにじゅういち", "c": "ゔぁあじょん にじゅういち", "d": "v21", "e": "ゔぃい21"}
CTX = {
 "1": ("もう一つ、{D} {v}で新しく加わった「AI」ボタンです。", True),
 "2": ("接続の管理は、{D} {v}におまかせ。", True),
 "3": ("すでに5社が、この機能のために、本番環境を{v}へ移行中です。", False),
}
jobs = dict(EN)
for k, v in V.items():
    for c, (tpl, with4d) in CTX.items():
        jobs[f"V{k}{c}"] = tpl.replace("{D}", D).replace("{v}", v)
c = client(); lines = []
for name, text in jobs.items():
    lines.append(f"{name}: {text}")
    with open(out/f"{name}.mp3", "wb") as w:
        for ch in c.text_to_speech.convert(voice, text=text, model_id="eleven_v4", language_code="ja", seed=1, output_format="mp3_44100_128"): w.write(ch)
(out/"options.txt").write_text("\n".join(lines)+"\n", encoding="utf-8"); print(len(jobs), "clips")
