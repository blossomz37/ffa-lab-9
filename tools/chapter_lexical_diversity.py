#!/usr/bin/env python3
"""
chapter_lexical_diversity.py
----------------------------
Compute lexical diversity metrics that editors and stylists use to gauge repetition and range.

USAGE
    python3 chapter_lexical_diversity.py path/to/chapter.txt --window 200 --json lex.json

WHAT IT REPORTS
- Tokens (N), Types/Vocabulary size (V), Hapax (V1), Dis legomena (V2)
- TTR (V/N), RootTTR (Guiraud R = V/sqrt(N)), Herdan's C (log V / log N), Maas a
- Approx MTLD (measure of textual lexical diversity) with threshold 0.72
- Moving-window TTR (window=N tokens), min/avg/max across the text
- Content vs Function ratio using a small stopword list

All standard library; heavily commented for learning.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

def tokens(text: str) -> List[str]:
    # Lowercased word tokens
    return [w.lower() for w in WORD_RE.findall(text.replace("\r\n","\n").replace("\r","\n"))]

# Small function-word list (add more as desired)
FUNCTION = {
    "the","a","an","and","or","but","if","then","else","of","to","in","on","for","with","as",
    "at","by","from","that","this","it","is","was","were","be","been","are","am","i","you",
    "he","she","they","we","my","your","his","her","their","our","not","no","so","do","did","does",
    "have","has","had","there","here","when","where","why","how","what","which","who","whom","whose"
}

@dataclass
class LexReport:
    N_tokens: int
    V_types: int
    V1_hapax: int
    V2_dis: int
    TTR: float
    RootTTR: float
    HerdanC: float
    MaasA: float
    MTLD_approx: float
    window_TTR_min: float
    window_TTR_avg: float
    window_TTR_max: float
    content_token_ratio: float

def type_token_stats(words: List[str]) -> Tuple[int,int,int,int]:
    N = len(words)
    c = Counter(words)
    V = len(c)
    V1 = sum(1 for w,f in c.items() if f == 1)
    V2 = sum(1 for w,f in c.items() if f == 2)
    return N, V, V1, V2

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def herdan_c(V: int, N: int) -> float:
    # C = log(V) / log(N)
    return safe_div(math.log(max(V,1)), math.log(max(N,1)))

def maas_a(V: int, N: int) -> float:
    # a = (log N - log V) / (log N)^2
    lnN = math.log(max(N,1))
    return safe_div(lnN - math.log(max(V,1)), lnN**2)

def moving_window_TTR(words: List[str], window: int) -> List[float]:
    if window <= 0:
        return []
    n = len(words)
    if n < window:
        return [safe_div(len(set(words)), len(words))] if words else []
    out = []
    for i in range(0, n - window + 1):
        seg = words[i:i+window]
        out.append(len(set(seg))/window)
    return out

def approx_mtld(words: List[str], threshold: float = 0.72) -> float:
    # Simple forward-only MTLD approximation (no bidirectional pass).
    if not words:
        return 0.0
    factors = 0
    types = set()
    count = 0
    for w in words:
        count += 1
        types.add(w)
        ttr = len(types) / count
        if ttr <= threshold:
            factors += 1
            types = set()
            count = 0
    # partial factor handling
    if count > 0:
        # proportion of remaining to hit threshold (linear assumption)
        partial = (ttr - threshold) / (1.0 - threshold) if (1.0 - threshold) > 0 else 0.0
        factors += partial
    return len(words) / max(factors, 1e-9)

def content_ratio(words: List[str]) -> float:
    if not words:
        return 0.0
    content = [w for w in words if w not in FUNCTION]
    return len(content) / len(words)

def analyze(text: str, window: int = 200) -> LexReport:
    words = tokens(text)
    N, V, V1, V2 = type_token_stats(words)
    TTR = safe_div(V, N)
    RootTTR = safe_div(V, math.sqrt(max(N,1)))
    C = herdan_c(V, N)
    a = maas_a(V, N)
    mtld = approx_mtld(words)
    win = moving_window_TTR(words, window)
    if win:
        win_min, win_avg, win_max = min(win), sum(win)/len(win), max(win)
    else:
        win_min = win_avg = win_max = 0.0
    cr = content_ratio(words)

    return LexReport(
        N_tokens=N, V_types=V, V1_hapax=V1, V2_dis=V2,
        TTR=round(TTR,3), RootTTR=round(RootTTR,3),
        HerdanC=round(C,3), MaasA=round(a,3),
        MTLD_approx=round(mtld,1),
        window_TTR_min=round(win_min,3),
        window_TTR_avg=round(win_avg,3),
        window_TTR_max=round(win_max,3),
        content_token_ratio=round(cr,3),
    )

def main() -> None:
    ap = argparse.ArgumentParser(description="Lexical diversity metrics for a chapter.")
    ap.add_argument("input", type=str, help="Path to chapter .txt")
    ap.add_argument("--window", type=int, default=200, help="Window size for moving TTR (tokens)")
    ap.add_argument("--json", type=str, default="", help="Write metrics to JSON")
    args = ap.parse_args()

    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    text = p.read_text(encoding="utf-8", errors="ignore")
    report = analyze(text, window=args.window)

    print("\n=== Lexical Diversity ===")
    print(f"File: {p}")
    print(f"N={report.N_tokens} | V={report.V_types} | Hapax={report.V1_hapax} | Dis={report.V2_dis}")
    print(f"TTR={report.TTR} | RootTTR={report.RootTTR} | HerdanC={report.HerdanC} | Maas a={report.MaasA}")
    print(f"MTLD≈ {report.MTLD_approx}")
    print(f"Moving TTR (win={args.window}) — min {report.window_TTR_min}, avg {report.window_TTR_avg}, max {report.window_TTR_max}")
    print(f"Content token ratio: {report.content_token_ratio}")

    if args.json:
        out = Path(args.json)
        out.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON written: {out.resolve()}")

if __name__ == "__main__":
    main()
