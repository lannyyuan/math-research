"""Generate the narration audio + per-line timing for a video.

Usage: python3 scripts/tts.py src/gas-car/narration.json public/voice/gas-car src/gas-car/voice-timing.json
Needs: pip install edge-tts   (Microsoft Edge online neural voices)

One TTS request per segment keeps the prosody natural; word-boundary events
are aligned back to the script lines so subtitles/highlights can start exactly
when each line is spoken.
"""
import asyncio
import json
import os
import subprocess
import sys

import certifi

# Respect a corporate / sandbox CA bundle if one is configured.
_ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
if _ca and os.path.exists(_ca):
    certifi.where = lambda: _ca  # edge-tts builds its SSL context from certifi

import edge_tts  # noqa: E402

PUNCT = set("，。！？、；：“”‘’（）《》…—,.!?;: \"'")


def strip(s: str) -> str:
    return "".join(ch for ch in s if ch not in PUNCT)


async def synth(text: str, voice: str, rate: str, pitch: str, out_mp3: str):
    comm = edge_tts.Communicate(
        text, voice, rate=rate, pitch=pitch, boundary="WordBoundary",
        proxy=os.environ.get("HTTPS_PROXY") or None,
    )
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 1e7,
                    "end": (chunk["offset"] + chunk["duration"]) / 1e7,
                })
    return words


def duration(path: str) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path,
    ])
    return float(out.strip())


def align(lines, words):
    """Map each script line to [start, end] using the word boundary stream."""
    # character index (punctuation stripped) -> word start/end
    char_start, char_end = [], []
    for w in words:
        n = len(strip(w["text"]))
        for _ in range(n):
            char_start.append(w["start"])
            char_end.append(w["end"])
    result = []
    pos = 0
    for line in lines:
        n = len(strip(line))
        if pos + n > len(char_start):
            raise RuntimeError(f"alignment failed for line: {line}")
        result.append({"text": line, "start": char_start[pos], "end": char_end[pos + n - 1]})
        pos += n
    return result


async def main(cfg_path: str, out_dir: str, timing_path: str):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    timing = {"voice": cfg["voice"], "segments": {}}
    for seg in cfg["segments"]:
        text = "".join(seg["lines"])
        mp3 = os.path.join(out_dir, f"{seg['id']}.mp3")
        words = await synth(text, cfg["voice"], cfg["rate"], cfg["pitch"], mp3)
        lines = align(seg["lines"], words)
        dur = duration(mp3)
        timing["segments"][seg["id"]] = {
            "file": os.path.basename(mp3),
            "duration": round(dur, 3),
            "lines": lines,
            "words": [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        }
        print(f"{seg['id']}: {dur:.2f}s  " + " | ".join(f"{l['start']:.2f}-{l['end']:.2f}" for l in lines))
    with open(timing_path, "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:4]))
