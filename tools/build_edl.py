#!/usr/bin/env python3
"""narration/*.mp3 の長さから、短縮版(ナレーション基準)の編集リスト 10min/edl.json を作る。
  python3 tools/build_edl.py /path/to/ffmpeg
各シーンの尺 = max(ナレーション+余白, 元動画の区間 / 最大倍速)。静止に近い S14 は倍速にせず、元動画の冒頭を等速で使う。"""
import sys, re, json, subprocess, math, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
PAD, LEAD, MAXSPEED, FR = 2.0, 0.8, 2.0, 25
sec = lambda s: int(s.split(":")[0])*60 + int(s.split(":")[1])
dur = lambda f: (lambda m: int(m[1])*3600+int(m[2])*60+float(m[3]))(re.search(r"Duration: (\d+):(\d+):([\d.]+)", subprocess.run([ff,"-hide_banner","-i",str(f)],capture_output=True,text=True).stderr))
# 元動画の区間は 03_ja_draft_10min.md の「元動画 a–b」から(最初の1回だけ。以後は edl.json を引き継ぐ)
edlf = root/"10min"/"edl.json"
if edlf.exists():
    src = {s["id"]: (s["src_a"], s["src_b"]) for s in json.loads(edlf.read_text())["scenes"]}
else:
    md = (root/"10min"/"03_ja_draft_10min.md").read_text(encoding="utf-8")
    src = {m[0]: (sec(m[1]), sec(m[2])) for m in re.findall(r"^## (S\d+) ｜.*?\n.*?元動画 (\d+:\d+)–(\d+:\d+)\*", md, re.M|re.S)}
scenes, t = [], 0.0
for sid in sorted(src):
    a, b = src[sid]; clip = dur(root/"10min"/"narration"/f"{sid}.mp3")
    still = sid == "S14"
    slot = clip + PAD + 2.0 if still else max(clip + PAD, (b - a)/MAXSPEED)
    slot = math.ceil(slot*FR)/FR
    scenes.append(dict(id=sid, src_a=a, src_b=b, clip=round(clip,2), slot=slot, start=round(t,2),
                       narr_at=round(t+LEAD,2), speed=1.0 if still else round((b-a)/slot,2), still=still))
    t += slot
edlf.write_text(json.dumps(dict(total=round(t,2), scenes=scenes), ensure_ascii=False, indent=1))
for s in scenes: print(s["id"], f'{s["start"]:6.1f}s slot {s["slot"]:5.1f}s clip {s["clip"]:5.1f}s speed x{s["speed"]}')
print("total", round(t,1), f"= {int(t//60)}:{int(t%60):02d}")
