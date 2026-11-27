#!/usr/bin/env python3
"""BGM の継ぎ目を、小節の頭(拍の区切り)に合わせて決める → 10min/bgm_plan.json
  python3 tools/plan_bgm.py /path/to/ffmpeg
・曲A→曲B→曲C をクロスフェード(1小節ぶん)でつなぐ。切る位置は「小節の頭」で、前後より音量が落ちる所を優先する。
・最後は、曲Cを「終わり側」に合わせて使い、曲自身の終止(フェードアウト)が動画の終わりに来るようにする。
・曲Aの頭は無音から立ち上げ、曲Cの終わりは曲の自然な減衰をそのまま使う。"""
import sys, json, subprocess, pathlib, numpy as np, librosa
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
d = root/"10min"; edl = json.loads((d/"edl.json").read_text()); st = {s["id"]: s["start"] for s in edl["scenes"]}; total = edl["total"]
SR = 22050
def find(k):
    for e in ("mp3", "m4a", "wav", "aac"):
        if (d/"bgm"/f"{k}.{e}").exists(): return d/"bgm"/f"{k}.{e}"
HINT = {"A": 94, "B": 98, "C": 92}   # Suno に指定した BPM(拍の数え違い(3/4倍など)を防ぐ)
def analyse(k):
    p = find(k)
    raw = subprocess.run([ff, "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    y = np.frombuffer(raw, np.float32); dur = len(y)/SR
    oenv = librosa.onset.onset_strength(y=y, sr=SR, hop_length=512)
    t0 = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=SR, hop_length=512, start_bpm=HINT[k], max_tempo=HINT[k]*1.12, ac_size=12))[0])
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=SR, hop_length=512, bpm=t0, tightness=200)
    tempo = float(np.atleast_1d(tempo)[0]); bt = librosa.frames_to_time(beats, sr=SR, hop_length=512)
    # 1小節 = 4拍。拍の位相は「強拍に onset が集まる位置」で決める
    ph = int(np.argmax([oenv[beats[i::4]].sum() for i in range(4)]))
    bars = bt[ph::4]
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    def bar_rms(t0, t1): return float(np.sqrt(np.mean(rms[int(t0*SR/512):max(int(t0*SR/512)+1, int(t1*SR/512))]**2)))
    br = [bar_rms(bars[i], bars[i+1]) for i in range(len(bars)-1)]
    return dict(path=p, dur=dur, tempo=tempo, bars=bars, rms=br)
def pick(a, target, win=6.0):
    """target 付近の小節の頭のうち、近くて音量が小さいもの(フレーズの切れ目)を選ぶ"""
    c = [(i, t) for i, t in enumerate(a["bars"][:-1]) if abs(t-target) <= win]
    if not c: i = int(np.argmin(abs(a["bars"]-target))); return float(a["bars"][i])
    r = np.array([a["rms"][i] for i, _ in c]); r = (r-r.min())/(r.max()-r.min()+1e-9)
    s = [abs(t-target)/win*0.6+r[k]*0.8 for k, (i, t) in enumerate(c)]
    return float(c[int(np.argmin(s))][1])
A, B, C = (analyse(k) for k in "ABC")
for n, x in zip("ABC", (A, B, C)): print(f"{n}: {x['dur']:.1f}s  テンポ {x['tempo']:.0f}BPM  小節 {len(x['bars'])}  1小節 {240/x['tempo']:.2f}s  最初の小節の頭 {x['bars'][0]:.2f}s")
XF = round(240/A["tempo"], 2)                      # 1小節
T0, T1 = st["S06"], st["S11"]
a_cut = pick(A, T0+XF)                              # 曲Aを切る小節の頭
b0 = float(B["bars"][0]) if B["bars"][0] < 3 else 0.0
oB = a_cut-XF                                       # 曲Bが動画で始まる時刻
b_cut = pick(B, b0+(T1+XF-oB))                      # 曲Bを切る小節の頭
oC = oB+(b_cut-b0)-XF                               # 曲Cが動画で始まる時刻
need = total-oC                                     # 曲Cが受け持つ長さ
tc_exact = C["dur"]-need
cand = [t for t in C["bars"] if t <= tc_exact+0.01]
tc = float(max(cand)) if cand else 0.0              # 終わり側に合わせる(少し手前の小節の頭 = 曲の終わりが動画の終わりより後)
plan = dict(xf=XF, total=total, tracks=[
    dict(file=A["path"].name, use_start=0.0, use_end=round(a_cut, 3)),
    dict(file=B["path"].name, use_start=round(b0, 3), use_end=round(b_cut, 3)),
    dict(file=C["path"].name, use_start=round(tc, 3), use_end=round(C["dur"], 3))])
(d/"bgm_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
def mm(t): return f"{int(t//60)}:{t%60:04.1f}"
print(f"\nA→B  A を {a_cut:.2f}s(小節の頭)で切る → B は動画の {mm(oB)} から  (シーン S06 は {mm(T0)})")
print(f"B→C  B を {b_cut:.2f}s で切る → C は動画の {mm(oC)} から  (シーン S11 は {mm(T1)})")
print(f"C: 曲の {tc:.2f}s(小節の頭)〜{C['dur']:.1f}s を使用。曲の終わりは動画の終わりの {C['dur']-tc-need:+.1f}s 後(動画 {mm(total)})")
