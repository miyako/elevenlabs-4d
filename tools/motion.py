#!/usr/bin/env python3
"""元動画の各フレームの「動き」(前フレームから大きく変わった画素数)を計算して 10min/motion.npy に保存する。
  python3 tools/motion.py /path/to/ffmpeg"""
import sys, subprocess, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
src = root.parent/"video"/"AI Agentic Framework 10-minute demo.mp4"
W, H = 480, 266
p = subprocess.Popen([ff, "-loglevel", "error", "-i", str(src), "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
prev, out = None, []
while True:
    b = p.stdout.read(W*H)
    if len(b) < W*H: break
    g = np.frombuffer(b, np.uint8).astype(np.int16)
    out.append(0 if prev is None else int((np.abs(g-prev) > 25).sum())); prev = g
np.save(root/"10min"/"motion.npy", np.array(out, np.int32)); print(len(out), "frames")
