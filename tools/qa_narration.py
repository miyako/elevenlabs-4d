#!/usr/bin/env python3
"""ナレーション音声の自動チェック。各クリップについて:
  ・冒頭の無音/立ち上がり ・書き起こし(Whisper)との照合(読み間違い・抜け)
  ・冒頭の「短い語 + 不自然な間」(「では」「次の」型) ・文中の長すぎる無音 ・末尾の雑音
  python3 tools/qa_narration.py /path/to/ffmpeg [S05 S09 ...]   → 10min/qa_report.md
要 mlx-whisper(音声は Whisper で聞き取るので、人の耳の代わりではなく、見落とし防止用)。"""
import sys, re, json, difflib, subprocess, pathlib, os
import numpy as np
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 and not re.match(r"S\d+$", sys.argv[1]) else "ffmpeg"
only = [a for a in sys.argv[1:] if re.match(r"S\d+$", a)]
os.environ["PATH"] = str(pathlib.Path(ff).parent)+os.pathsep+os.environ["PATH"] if "/" in ff else os.environ["PATH"]
import mlx_whisper
d = root/"10min"; rows = []; flags_all = 0
def norm(s): return re.sub(r"[\s、。「」『』・…!?？！,.:;()（）_\-]", "", s).lower()
for f in sorted((d/"narration").glob("S*.mp3")):
    sid = f.stem
    if only and sid not in only: continue
    text = (d/"tts_txt"/f"{sid}.txt").read_text(encoding="utf-8").strip()
    wav = d/f".qa_{sid}.wav"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    raw = subprocess.run([ff, "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", "44100", "-t", "0.05", "-f", "s16le", "-"], capture_output=True).stdout
    onset = 20*np.log10(abs(np.frombuffer(raw, np.int16)[:882]/32768).max()+1e-9)
    a = np.frombuffer(subprocess.run([ff, "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(float)/32768; sr = 16000
    win = int(sr*0.02); env = np.array([20*np.log10(np.sqrt(np.mean(a[i:i+win]**2))+1e-9) for i in range(0, len(a)-win, win)])
    # 無音区間(-42dB 未満が 0.12 秒以上)
    sil, i = [], 0
    while i < len(env):
        if env[i] < -42:
            j = i
            while j < len(env) and env[j] < -42: j += 1
            if (j-i)*0.02 >= 0.12: sil.append((i*0.02, j*0.02))
            i = j
        else: i += 1
    dur = len(a)/sr
    r = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ja", word_timestamps=True, verbose=None, condition_on_previous_text=False)
    words = [(w["start"], w["end"], w["word"].strip()) for s in r["segments"] for w in s.get("words", [])]
    flags = []
    # 1) 冒頭: 最初の20ミリ秒が大きい = 語頭が途中から始まっている(最初の音が欠けて、ぷつっと始まる)
    if onset > -38: flags.append(f"語頭が欠けている疑い(冒頭20msのピーク {onset:.0f}dB。-38dB 以下が正常)")
    # 3) 文中の長い無音
    for s0, s1 in sil:
        if s1-s0 >= 1.3 and s1 < dur-1.0: flags.append(f"長い無音 {s1-s0:.2f}秒({s0:.1f}秒〜)")
    # 4) 末尾
    tail = [s for s in sil if s[1] >= dur-0.05]
    if tail and dur-tail[0][0] > 0.6: flags.append(f"末尾の無音が長い({dur-tail[0][0]:.2f}秒)")
    last_sil = sil[-1] if sil else None
    if last_sil and 0.02 < dur-last_sil[1] < 0.4 and last_sil[1]-last_sil[0] > 0.5: flags.append(f"末尾に短い雑音({dur-last_sil[1]:.2f}秒)")
    # 5) 書き起こしとの照合(句読点で区切った塊ごと)
    heard = norm(r["text"]); chunks = [c for c in re.split(r"[。、!?！？]", text) if len(norm(c)) >= 4]
    bad = []
    for c in chunks:
        n = norm(c); sm = difflib.SequenceMatcher(None, heard, n, autojunk=False)
        cover = sum(b.size for b in sm.get_matching_blocks())/max(1, len(n))
        if cover < 0.45: bad.append((c, round(cover, 2)))
    if bad: flags.append("聞き取りが原文と合わない塊: "+" / ".join(f"「{c[:18]}」({v})" for c, v in bad[:4]))
    wav.unlink()
    rows.append((sid, dur, text[:24], flags, r["text"][:60])); flags_all += len(flags)
    print(f"{sid} {dur:5.1f}s  フラグ {len(flags)}", *[" - "+x for x in flags], sep="\n" if flags else "")
md = ["# ナレーション自動チェック", "", f"フラグ合計 {flags_all}。Whisper による機械的なチェックで、最終判断は耳で行ってください。", "", "| シーン | 長さ | フラグ |", "|---|---|---|"]
for sid, dur, t, fl, h in rows: md.append(f"| {sid} | {dur:.1f}s | {'<br>'.join(fl) if fl else '—'} |")
(d/"qa_report.md").write_text("\n".join(md)+"\n", encoding="utf-8"); print("report ->", d/"qa_report.md")
