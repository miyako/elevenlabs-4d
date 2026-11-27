#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""短縮版の映像を作る。ルールは次の3つだけ:
  1. 静止フレーム(画面に動きがない区間)だけを、削る(トリム)か、延ばす(ホールド)。
  2. 動いているフレームは、再生速度を変える場合だけ変える(既定は等速。どうしても足りないときだけ最大1.5倍速)。
  3. それ以外の加工はしない(カーソルの加工、ぼかし、クロスフェードなし)。
シーンのつなぎ目は、静止区間の中に置く(同じ画面どうしをつなぐので、切れ目が見えない)。
  python3 tools/edit_video.py /path/to/ffmpeg
出力: 10min/video_edit.mp4 と、音声合わせ用の 10min/edl.json"""
import sys, re, json, math, subprocess, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
d = root/"10min"; FPS = 25; W, H = 1920, 1062
PAD, PAD_LAST, LEAD, STOP_THR, MIN_STOP, KEEP_MIN, KEEP_FLOOR, SMAX, SNAP_RANGE = 2.0, 4.0, 0.8, 8, 10, 10, 6, 1.5, 12.0
m = np.load(d/"motion.npy"); NF = len(m)
old = json.loads((d/"edl.json").read_text())["scenes"]
ids = [s["id"] for s in old]; nominal = [s["src_a"] for s in old] + [NF/FPS]
dur = lambda f: (lambda x: int(x[1])*3600+int(x[2])*60+float(x[3]))(re.search(r"Duration: (\d+):(\d+):([\d.]+)", subprocess.run([ff, "-hide_banner", "-i", str(f)], capture_output=True, text=True).stderr))
clip = {i: dur(d/"narration"/f"{i}.mp3") for i in ids}
def runs(a, b):
    out, i = [], a
    while i < b:
        if m[i] <= STOP_THR:
            j = i
            while j < b and m[j] <= STOP_THR: j += 1
            out.append((i, j)); i = j
        else: i += 1
    return out
allstops = [r for r in runs(0, NF) if r[1]-r[0] >= MIN_STOP]
# --- つなぎ目を静止区間にそろえる
bounds = [0]
for k in range(1, len(ids)):
    B = int(round(nominal[k]*FPS))
    best = min(allstops, key=lambda r: 0 if r[0] <= B < r[1] else min(abs(r[0]-B), abs(r[1]-B)))
    snapped = B if best[0]+3 <= B < best[1]-3 else (best[0]+best[1])//2
    bounds.append(snapped)
    print(f"{ids[k]} つなぎ目 {B/FPS:6.1f}s → {snapped/FPS:6.1f}s ({(snapped-B)/FPS:+.1f}s) 静止 {(best[1]-best[0])/FPS:.1f}s")
bounds.append(NF)
# --- シーンごとの計画
seq, scenes, t = [], [], 0.0
for k, sid in enumerate(ids):
    a, b = bounds[k], bounds[k+1]; L = b-a
    T = clip[sid]+(PAD_LAST if sid == ids[-1] else PAD); Tf = math.ceil(T*FPS)
    st = [(max(r[0], a), min(r[1], b)) for r in runs(a, b) if min(r[1], b)-max(r[0], a) >= MIN_STOP]
    keep = {r: r[1]-r[0] for r in st}                      # 各静止区間で残すフレーム数
    def total(): return L-sum(r[1]-r[0]-keep[r] for r in st)
    speed = 1.0
    if Tf < L:
        need = L-Tf                                         # 削りたいフレーム数
        lo, hi = KEEP_MIN, max([r[1]-r[0] for r in st] or [KEEP_MIN])
        def cut(level): return sum(max(0, (r[1]-r[0])-level) for r in st)
        level = hi
        while level > lo and cut(level) < need: level -= 1  # 長い静止区間から順に削る(水位法)
        if cut(level) < need:                               # 最低保持まで削っても足りない場合
            lv = level
            while lv > KEEP_FLOOR and cut(lv) < need: lv -= 1
            level = lv
        for r in st: keep[r] = min(r[1]-r[0], level)
        left = total()
        if left > Tf:                                       # それでも長ければ、動いている部分だけ倍速
            speed = min(SMAX, left/Tf); Tf = math.ceil(left/speed)
    idx = []
    for f in range(a, b):                                   # 残すフレーム列(静止区間は中央を削る)
        r = next((r for r in st if r[0] <= f < r[1]), None)
        if r:
            kk = keep[r]; o = f-r[0]; ln = r[1]-r[0]
            if o < kk//2 or o >= ln-(kk-kk//2): idx.append(f)
        else: idx.append(f)
    if speed > 1.0:
        n = int(round(len(idx)/speed)); idx = [idx[min(len(idx)-1, int(round(i*speed)))] for i in range(n)]
    if len(idx) < Tf:                                       # 足りなければ最後(静止区間内)をホールド
        idx += [idx[-1]]*(Tf-len(idx))
    elif len(idx) > Tf and speed == 1.0:
        idx = idx[:Tf]
    scenes.append(dict(id=sid, src_a=round(a/FPS, 2), src_b=round(b/FPS, 2), clip=round(clip[sid], 2), slot=len(idx)/FPS,
                       start=round(t, 2), narr_at=round(t+LEAD, 2), speed=round(speed, 2), still=False))
    seq += idx; t += len(idx)/FPS
    print(f"{sid}: 元 {L/FPS:5.1f}s → {len(idx)/FPS:5.1f}s (ナレーション {clip[sid]:.1f}s) 倍速 x{speed:.2f}  静止区間 {len(st)}個")
total_s = len(seq)/FPS
(d/"edl.json").write_text(json.dumps(dict(total=round(total_s, 2), scenes=scenes), ensure_ascii=False, indent=1))
print(f"合計 {int(total_s//60)}:{total_s%60:04.1f}")
np.save(d/"seq.npy", np.array(seq, np.int32))
if "--plan" in sys.argv: sys.exit()
# --- 書き出し(フレームをそのまま並べ替えるだけ)
src = root.parent/"video"/"AI Agentic Framework 10-minute demo.mp4"
dec = subprocess.Popen([ff, "-loglevel", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", str(d/"video_edit.mp4")], stdin=subprocess.PIPE)
p, f = 0, 0
while p < len(seq):
    buf = dec.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    while p < len(seq) and seq[p] == f: enc.stdin.write(buf); p += 1
    f += 1
enc.stdin.close(); enc.wait(); print("wrote", d/"video_edit.mp4")
