#!/usr/bin/env python3
"""ナレーション末尾の無音と、ElevenLabs が付ける末尾の小さな雑音(息つぎ・クリック)を切る。
  python3 tools/trim_narration.py /path/to/ffmpeg   (10min/narration/*.mp3 を直接書き換える)
最後の無音が終端まで続いている場合だけ、無音の開始 + 0.25 秒で切る。"""
import sys, re, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
for f in sorted((root/"10min"/"narration").glob("S*.mp3")):
    err = subprocess.run([ff, "-hide_banner", "-i", str(f), "-af", "silencedetect=n=-40dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err); dur = int(m[1])*3600+int(m[2])*60+float(m[3])
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if not st: continue
    ls, le = st[-1], (en[-1] if len(en) == len(st) else dur)
    if dur-le <= 0.3 and ls > 1.0 and dur-(ls+0.25) > 0.1:
        tmp = f.with_suffix(".tmp.mp3")
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(f), "-t", f"{ls+0.25:.3f}", "-c", "copy", str(tmp)], check=True); tmp.replace(f)
        print(f"{f.name}: {dur:.2f}s -> {ls+0.25:.2f}s")
    else: print(f"{f.name}: そのまま ({dur:.2f}s)")
