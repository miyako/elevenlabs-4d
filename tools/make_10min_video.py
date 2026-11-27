#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""edl.json に従い、短縮版の動画を作る。ナレーション(と、あれば BGM)をミックスして mp4 にする。
  python3 tools/make_10min_video.py /path/to/ffmpeg
BGM: 10min/bgm/A, B, C(mp3/m4a/wav)があれば 3秒のクロスフェードでつなぎ、ナレーションの下に小さく流す。"""
import sys, json, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
BGM_GAIN = 0.3   # BGMの音量(一定。声があっても下げない)
d = root/"10min"; edl = json.loads((d/"edl.json").read_text()); sc = edl["scenes"]; total = edl["total"]
src = d/"video_edit.mp4"      # edit_video.py が作った映像(音声なし)
f = []
args = [ff, "-y", "-i", str(src)]
for s in sc: args += ["-i", str(d/"narration"/f"{s['id']}.mp3")]
def _bgm(k):
    for e in ("mp3", "m4a", "wav", "aac"):
        if (d/"bgm"/f"{k}.{e}").exists(): return d/"bgm"/f"{k}.{e}"
bgm = [p for p in (_bgm(k) for k in "ABC") if p]
for b in bgm: args += ["-i", str(b)]
labs = ""
for i, s in enumerate(sc):
    ms = int(s["narr_at"]*1000)
    f.append(f"[{i+1}:a]aformat=sample_rates=44100:channel_layouts=stereo,afade=t=in:d=0.04,adelay={ms}|{ms}[a{i}]"); labs += f"[a{i}]"
f.append(f"{labs}amix=inputs={len(sc)}:normalize=0,apad=whole_dur={total}[nar]")
if bgm:
    plan = json.loads((d/"bgm_plan.json").read_text())      # tools/plan_bgm.py が、小節の頭に合わせて決めた切り位置
    XF = plan["xf"]; n0 = len(sc)+1
    for j, tr in enumerate(plan["tracks"]):
        f.append(f"[{n0+j}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim={tr['use_start']}:{tr['use_end']},asetpts=PTS-STARTPTS[b{j}]")
    cur = "[b0]"
    for j in range(1, len(plan["tracks"])):
        f.append(f"{cur}[b{j}]acrossfade=d={XF}:c1=qsin:c2=qsin[x{j}]"); cur = f"[x{j}]"
    f.append(f"{cur}atrim=0:{total},afade=t=in:d=1.5,afade=t=out:st={total-3.0}:d=3.0:curve=qsin,volume={BGM_GAIN}[bg]")
    f.append("[nar][bg]amix=inputs=2:normalize=0[a]")   # ダッキングなし: BGMは一定の音量
else:
    f.append("[nar]anull[a]")
out = d/("demo_10min_final.mp4")
args += ["-filter_complex", ";".join(f), "-map", "0:v", "-map", "[a]", "-t", str(total),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)]
subprocess.run(args, check=True)
print("wrote", out, "| BGM:", [b.name for b in bgm] or "なし")
