#!/usr/bin/env python3
"""
chapter_beats_detection.py
--------------------------
Heuristic *beat detection* for a single chapter.
Looks for common narrative signals: setup, inciting incident, rising complications,
midpoint turn, crisis/climax, and resolution/exit hook.

This is a light, rule-based pass—useful as a sanity-check, not a replacement for craft.

USAGE
    python3 chapter_beats_detection.py path/to/chapter.txt --json beats.json

WHAT IT DOES
- Splits into sentences; scores each sentence for membership in beat categories via keyword cues.
- Applies position weighting (e.g., early hits favored for Setup/Inciting; late hits for Climax/Resolution).
- Returns top candidate sentences per beat with indices and brief reasons.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Tuple

SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

def sentences(text: str) -> List[str]:
    t = re.sub(r"\s+"," ", text.replace("\r\n","\n").replace("\r","\n").strip())
    return [s.strip() for s in SPLIT_RE.split(t) if s.strip()]

def toks(s: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(s)]

# Keyword cues per beat (expand per genre)
CUES = {
    "setup": {"introduce","arrive","daily","routine","normal","ordinary","establish","show","meet"},
    "inciting": {"discover","found","missing","murder","accident","message","mysterious","appears","vanish","dead","call"},
    "rising": {"but","however","then","complication","obstacle","because","therefore","after","as","meanwhile"},
    "midpoint": {"realize","truth","reveal","shift","decide","commit","point","halfway","now","must"},
    "crisis_climax": {"confront","fight","chase","corner","trap","choose","risk","sacrifice","final","climax","explode","collapse"},
    "resolution_hook": {"after","finally","at last","quiet","morning","later","return","home","resolve","yet","still","until","next"},
}

WEIGHTS = {
    "setup": (0.0, 0.25),
    "inciting": (0.05, 0.35),
    "rising": (0.2, 0.7),
    "midpoint": (0.45, 0.55),
    "crisis_climax": (0.7, 0.95),
    "resolution_hook": (0.85, 1.01),
}

@dataclass
class BeatHit:
    index: int
    score: float
    reason: str
    text: str

def in_window(pos: float, lo: float, hi: float) -> float:
    # triangular weighting: peak at center of [lo, hi]
    if pos < lo or pos > hi: 
        return 0.5  # small penalty for out-of-window, not zero
    center = (lo + hi) / 2.0
    # normalized distance from center
    d = abs(pos - center) / max(1e-9, (hi - lo)/2.0)
    return max(0.1, 1.0 - d)  # at least a little weight

def score_sentence(idx: int, s: str, pos: float) -> Dict[str, BeatHit]:
    w = toks(s)
    hits: Dict[str, BeatHit] = {}
    for beat, cue_words in CUES.items():
        cue_score = sum(1 for t in w if t in cue_words)
        if cue_score == 0:
            continue
        pos_weight = in_window(pos, *WEIGHTS[beat])
        sc = cue_score * (0.6 + 0.4*pos_weight)
        reason = f"{cue_score} cue(s), pos_weight={pos_weight:.2f}"
        hits[beat] = BeatHit(index=idx, score=round(sc,3), reason=reason, text=s)
    return hits

def analyze(text: str, top_k: int = 3) -> Dict[str, List[BeatHit]]:
    sents = sentences(text)
    n = len(sents) or 1
    candidates: Dict[str, List[BeatHit]] = {k: [] for k in CUES}

    for i, s in enumerate(sents):
        pos = (i+1) / n  # 0..1 position
        sh = score_sentence(i, s, pos)
        for k, hit in sh.items():
            candidates[k].append(hit)

    # take top K per beat
    for k in candidates:
        candidates[k] = sorted(candidates[k], key=lambda h: h.score, reverse=True)[:top_k]
    return candidates

def main() -> None:
    ap = argparse.ArgumentParser(description="Heuristic beat detection for a chapter.")
    ap.add_argument("input", type=str, help="Path to chapter .txt")
    ap.add_argument("--json", type=str, default="", help="Write detected beats to JSON")
    args = ap.parse_args()

    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    text = p.read_text(encoding="utf-8", errors="ignore")
    cand = analyze(text)

    print("\n=== Beat Detection (heuristic) ===")
    print(f"File: {p}")
    for beat, hits in cand.items():
        print(f"\n[{beat}]")
        if not hits:
            print("  (no clear candidates)")
            continue
        for h in hits:
            print(f"  - idx {h.index} | score {h.score} | {h.reason}")
            print(f"    \"{h.text}\"")

    if args.json:
        out = Path(args.json)
        payload = {k: [asdict(h) for h in v] for k, v in cand.items()}
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON written: {out.resolve()}")

if __name__ == "__main__":
    main()
