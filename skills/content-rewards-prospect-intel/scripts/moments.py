#!/usr/bin/env python3
"""Estimate "clippable moments per hour" from a transcript. This is a HEURISTIC that needs calibration
against real outcomes before you quote it to a client.

Usage:
  python3 moments.py transcript.vtt [--window 60 --step 15 --top 10]
  python3 moments.py transcript.srt
  python3 moments.py transcript.txt --minutes 62     (plain text: give the duration)

Transcript sources, cheapest first: the show's own transcript (podcast RSS <podcast:transcript> tag or
episode page), YouTube captions (yt-dlp --write-auto-subs --skip-download --sub-format vtt URL),
then local WhisperX / whisper.cpp (needs a GPU or a lot of CPU time; deep mode only).

How a window is scored (0-100). The signals mirror what OSS clippers score (SamurAI AI-Youtube-Shorts-Generator,
toki-plus/ai-highlight-clip, AgriciDaniel/claude-shorts: hook, standalone coherence, emotion, value density,
payoff), approximated without an LLM:
  hook (25)       window opens with a question, a contrarian marker ("nobody", "the truth is", "most people")
                  or a number
  density (25)    numbers, money, percentages and capitalised entities per 100 words
  emotion (20)    strong-sentiment and story words (failed, insane, fired, quit, million, never, secret...)
  standalone (15) few dangling references at the start ("that", "it", "so yeah", "like I said")
  payoff (15)     window ends on a complete sentence, with a conclusion marker ("that's why", "the lesson")
Overlapping windows are collapsed (greedy, highest first), and windows of 50+ count as candidates.

Output: candidates per hour (low/median/high across three thresholds), top windows with timestamps and text.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

HOOK = re.compile(r"^\W*(why|how|what|who|nobody|no one|the truth|most people|here'?s|the secret|stop|never|"
                  r"everyone|if you|the (biggest|real|number one)|\d)", re.I)
EMO = re.compile(r"\b(insane|crazy|fail(ed|ure)?|fired|quit|broke|million|billion|never|secret|mistake|"
                 r"scared|afraid|shock(ed|ing)?|hate|love|died|lost|won|wrong|lie|lied|truth|biggest|worst|"
                 r"best|changed my life|cried|laughed)\b", re.I)
DANGLING = re.compile(r"^\W*(and|but|so|that|it|this|they|he|she|like i said|as i said|exactly|right|yeah)\b", re.I)
PAYOFF = re.compile(r"(that'?s why|the lesson|so the point|bottom line|the key is|which means|and that'?s how)", re.I)
NUM = re.compile(r"(\$?\d[\d,.]*\s?(k|m|bn|%|percent|million|billion|thousand)?)", re.I)
ENT = re.compile(r"(?<![.!?]\s)\b[A-Z][a-z]{2,}\b")


def parse(path: str, minutes: float | None):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    cues = []
    ts = re.compile(r"(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{3})")
    blocks = re.split(r"\n\s*\n", raw)
    last_end = 0.0
    for b in blocks:
        m = ts.search(b)
        if not m:
            continue
        h = int((m.group(1) or "0:")[:-1])
        start = h * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
        text = " ".join(line for line in b[m.end():].splitlines() if line.strip() and "-->" not in line)
        text = re.sub(r"<[^>]+>", "", text).strip()
        end = int((m.group(5) or "0:")[:-1]) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000
        last_end = max(last_end, end)
        if text and (not cues or text != cues[-1][1]):  # YouTube auto-captions repeat lines
            cues.append((start, text))
    if cues:
        return cues, max(last_end, cues[-1][0])
    if not minutes:
        sys.exit("plain-text transcript: pass --minutes so timing can be estimated")
    words = raw.split()
    per = minutes * 60 / max(1, len(words))
    sents = re.split(r"(?<=[.!?])\s+", raw)
    t, out = 0.0, []
    for s in sents:
        out.append((t, s.strip()))
        t += len(s.split()) * per
    return out, minutes * 60


def score(text: str) -> tuple[int, dict]:
    words = max(1, len(text.split()))
    s = {
        "hook": 25 if HOOK.search(text[:120]) else 0,
        "density": min(25, int((len(NUM.findall(text)) * 3 + len(ENT.findall(text))) / words * 100 * 1.5)),
        "emotion": min(20, len(EMO.findall(text)) * 5),
        "standalone": 0 if DANGLING.search(text[:40]) else 15,
        "payoff": 15 if (PAYOFF.search(text) and text.rstrip()[-1:] in ".!?") else (7 if text.rstrip()[-1:] in ".!?" else 0),
    }
    return sum(s.values()), s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--minutes", type=float)
    ap.add_argument("--window", type=int, default=60); ap.add_argument("--step", type=int, default=15)
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    cues, dur = parse(a.path, a.minutes)
    wins, t = [], 0.0
    while t < dur:
        text = " ".join(c[1] for c in cues if t <= c[0] < t + a.window)
        if len(text.split()) >= 40:
            sc, parts = score(text)
            wins.append({"start": round(t), "end": round(t + a.window), "score": sc, "parts": parts, "text": text[:400]})
        t += a.step
    wins.sort(key=lambda w: -w["score"])
    hours = max(dur / 3600, 1 / 60)

    def count(th):
        chosen = []
        for w in wins:
            if w["score"] >= th and all(w["end"] <= c["start"] or w["start"] >= c["end"] for c in chosen):
                chosen.append(w)
        return chosen
    res = {th: len(count(th)) / hours for th in (40, 50, 60)}
    top = count(40)[: a.top]
    json.dump({
        "duration_min": round(dur / 60, 1), "windows_scored": len(wins),
        "clippable_moments_per_hour": {"high_estimate(>=40)": round(res[40], 1), "median(>=50)": round(res[50], 1),
                                       "low_estimate(>=60)": round(res[60], 1)},
        "top_windows": [{"at": f"{w['start'] // 60}:{w['start'] % 60:02d}", **{k: w[k] for k in ('score', 'parts', 'text')}}
                        for w in top],
        "label": "HEURISTIC estimate from transcript signals only. Calibrate against real clip performance before quoting.",
    }, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
