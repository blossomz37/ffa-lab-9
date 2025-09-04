#!/usr/bin/env python3
"""
chapter_emotion_arc.py
----------------------
Estimate a chapter's *emotion arc* using tiny lexicons and rolling averages.
Signals include overall valence (positive/negative) and Plutchik-ish buckets
(joy, sadness, anger, fear, trust, disgust, surprise, anticipation).

This is intentionally lightweight and heuristic—good for trendlines, not diagnosis.
No external libraries required.

USAGE
    python3 chapter_emotion_arc.py path/to/chapter.txt --window 5 --csv arc.csv --json arc.json

WHAT IT DOES
- Splits text into sentences (simple regex).
- Scores each sentence by tallying lexicon hits:
    * valence: +1 positive word, -1 negative word (tiny list below).
    * emotions: count per category.
- Computes rolling averages over a configurable window size.
- Emits per-sentence and rolling metrics to CSV/JSON (optional) and prints a summary.

TIP
- Expand the tiny lexicons for your genre to improve signal.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import List, Dict

SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

def sentences(text: str) -> List[str]:
    t = re.sub(r"\s+"," ", text.replace("\r\n","\n").replace("\r","\n").strip())
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(t) if s.strip()]

def tokens(s: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(s)]

# --- Tiny lexicons (extend as needed) ---
POS = {"joy","love","glad","hope","delight","cheer","smile","trust","safe","calm","relief","brave","confident","win"}
NEG = {"sad","angry","anger","fear","afraid","terror","panic","hurt","bleed","pain","cry","fail","lose","danger","threat"}

EMO = {
    "joy": {"joy","delight","happy","glad","smile","cheer","pleased","laugh","grin"},
    "sadness": {"sad","sorrow","gloom","mourn","cry","tears","grief","lonely"},
    "anger": {"anger","angry","rage","fury","irritate","annoyed","hate","jealous"},
    "fear": {"fear","afraid","scare","terror","panic","anxiety","dread","threat"},
    "trust": {"trust","safe","secure","faith","reliance","certain"},
    "disgust": {"disgust","gross","nausea","repulse","vile","filthy","revolt"},
    "surprise": {"surprise","shock","startle","astonish","sudden","unexpected"},
    "anticipation": {"anticipate","eager","expect","await","hope","yearn","ready"},
}

@dataclass
class SentenceScore:
    index: int
    text: str
    valence_raw: int
    emotions: Dict[str,int]

@dataclass
class ArcSummary:
    sentences: int
    avg_valence: float
    top_emotions: List[str]  # ranked by total counts

def score_sentence(i: int, s: str) -> SentenceScore:
    toks = tokens(s)
    val = sum(1 for w in toks if w in POS) - sum(1 for w in toks if w in NEG)
    emo_counts = {k: sum(1 for w in toks if w in v) for k, v in EMO.items()}
    return SentenceScore(index=i, text=s, valence_raw=val, emotions=emo_counts)

def rolling(values: List[float], window: int) -> List[float]:
    if window <= 1:
        return values[:]
    out = []
    dq = deque()
    run = 0.0
    for v in values:
        dq.append(v); run += v
        if len(dq) > window:
            run -= dq.popleft()
        out.append(run/len(dq))
    return out

def analyze(text: str, window: int = 5):
    sents = sentences(text)
    scores = [score_sentence(i, s) for i, s in enumerate(sents)]
    val_raw = [sc.valence_raw for sc in scores]
    val_roll = rolling(val_raw, window)

    # emotion totals and rolling per emotion
    emo_totals = Counter()
    emo_series = {k: [] for k in EMO}
    for sc in scores:
        for k, c in sc.emotions.items():
            emo_series[k].append(float(c))
            emo_totals[k] += c
    emo_roll = {k: rolling(v, window) for k, v in emo_series.items()}

    top_emotions = [k for k,_ in emo_totals.most_common(3)]
    summary = ArcSummary(sentences=len(sents), avg_valence=round(mean(val_raw),2) if val_raw else 0.0, top_emotions=top_emotions)
    return scores, val_roll, emo_roll, summary

def main() -> None:
    ap = argparse.ArgumentParser(description="Emotion arc via tiny lexicons and rolling averages.")
    ap.add_argument("input", type=str, help="Path to chapter .txt")
    ap.add_argument("--window", type=int, default=5, help="Rolling window size (sentences)")
    ap.add_argument("--csv", type=str, default="", help="Write per-sentence & rolling metrics to CSV")
    ap.add_argument("--json", type=str, default="", help="Write summary + series to JSON")
    args = ap.parse_args()

    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    text = p.read_text(encoding="utf-8", errors="ignore")
    scores, val_roll, emo_roll, summary = analyze(text, window=args.window)

    print("\n=== Emotion Arc ===")
    print(f"File: {p}")
    print(f"Sentences: {summary.sentences} | Avg valence: {summary.avg_valence} | Top emotions: {summary.top_emotions}")
    print(f"(Rolling window = {args.window})")

    if args.csv:
        out = Path(args.csv)
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            header = ["sent_index","valence_raw","valence_rolling"] + [f"{k}_rolling" for k in EMO]
            w.writerow(header)
            for i, sc in enumerate(scores):
                row = [sc.index, sc.valence_raw, round(val_roll[i],3) if i < len(val_roll) else ""]
                for k in EMO:
                    row.append(round(emo_roll[k][i],3) if i < len(emo_roll[k]) else "")
                w.writerow(row)
        print(f"CSV written: {out.resolve()}")

    if args.json:
        outj = Path(args.json)
        payload = {
            "summary": asdict(summary),
            "valence_rolling": val_roll,
            "emotions_rolling": emo_roll,
        }
        outj.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON written: {outj.resolve()}")

if __name__ == "__main__":
    main()
