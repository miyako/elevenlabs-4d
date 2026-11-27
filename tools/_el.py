"""共通: プロジェクト直下の .env を読み込み(中身は表示しない)、ElevenLabs クライアントを返す。"""
import os, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
def client():
    envf = ROOT/".env"
    if envf.exists():
        for l in envf.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    from elevenlabs import ElevenLabs
    return ElevenLabs()
