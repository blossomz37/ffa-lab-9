#!/usr/bin/env python3
"""
chapter_mechanics_cleanup.py
----------------------------
Mechanics & cleanup checks an editor typically notes.

WHAT THIS SCRIPT CHECKS
- Punctuation overuse (counts & density per 1k words):
    * Exclamation marks, question marks, ellipses (... or …), em/en dashes, multi-punct ("?!", "!!", "??")
- Typography consistency:
    * Straight vs curly quotes; mixed usage
    * Hyphen vs en dash vs em dash; spaced dashes (" - ")
    * Non‑breaking spaces, tabs, double spaces
- Spacing & layout hygiene:
    * Leading/trailing spaces on lines, blank line runs
- Repetition:
    * Immediate duplicate words ("the the"), top repeated words overall,
      sliding-window repeats (same word appearing too frequently in a small window)
- Unmatched punctuation:
    * Parentheses (), brackets [], braces {}, quotes ""/''
- Optional normalization:
    * --write_normalized / --style plain|smart
      - plain: straight quotes, triple dot ellipses, em dash as '—', collapse spaces
      - smart: curly quotes, ellipsis '…', em dash '—', tidy spacing

USAGE
    python3 chapter_mechanics_cleanup.py path/to/chapter.txt --json out.json
    # Optional normalized output:
    python3 chapter_mechanics_cleanup.py path/to/chapter.txt --write_normalized fixed.txt --style smart

NOTES
- Heuristics, not verdicts. Review diffs before accepting changes.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

# ---------------
# Normalization
# ---------------
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n","\n").replace("\r","\n")

def tokens(text: str) -> List[str]:
    return WORD_RE.findall(text)

def density_per_1k(count: int, total_words: int) -> float:
    return round((count / total_words * 1000), 2) if total_words else 0.0

# ---------------
# Core checks
# ---------------
def punctuation_overuse(text: str, total_words: int) -> Dict[str, Dict[str, float]]:
    # Count various punctuation signals
    exclam = text.count("!")
    qmark  = text.count("?")
    ellips = text.count("...") + text.count("…")
    emdash = text.count("—")
    endash = text.count("–")
    spaced_dash = len(re.findall(r"\s-\s", text))
    multi_punct = len(re.findall(r"[!?]{2,}|!\?|!\?!|\?!", text))

    return {
        "exclamations": {"count": exclam, "per_1k_words": density_per_1k(exclam, total_words)},
        "question_marks": {"count": qmark, "per_1k_words": density_per_1k(qmark, total_words)},
        "ellipses": {"count": ellips, "per_1k_words": density_per_1k(ellips, total_words)},
        "em_dashes": {"count": emdash, "per_1k_words": density_per_1k(emdash, total_words)},
        "en_dashes": {"count": endash, "per_1k_words": density_per_1k(endash, total_words)},
        "spaced_hyphen_as_dash": {"count": spaced_dash, "per_1k_words": density_per_1k(spaced_dash, total_words)},
        "multi_punct": {"count": multi_punct, "per_1k_words": density_per_1k(multi_punct, total_words)},
    }

def typography_issues(text: str) -> Dict[str, int]:
    straight = text.count('"') + text.count("'")
    curly = text.count("“") + text.count("”") + text.count("‘") + text.count("’")
    hyphen = text.count("-")
    endash = text.count("–")
    emdash = text.count("—")
    spaced_dash = len(re.findall(r"\s-\s", text))
    nbsp = text.count("\xa0")
    tabs = text.count("\t")
    double_space = len(re.findall(r"  +", text))

    return {
        "straight_quotes": straight,
        "curly_quotes": curly,
        "hyphens": hyphen,
        "en_dashes": endash,
        "em_dashes": emdash,
        "spaced_hyphen_as_dash": spaced_dash,
        "nonbreaking_spaces": nbsp,
        "tabs": tabs,
        "double_spaces": double_space,
    }

def spacing_layout(text: str) -> Dict[str, int]:
    lines = text.split("\n")
    leading_trailing = sum(1 for ln in lines if ln.startswith(" ") or ln.endswith(" "))
    blank_runs = len(re.findall(r"\n{3,}", text))  # 3+ blank lines in a row
    return {"lines_with_edge_spaces": leading_trailing, "blank_line_runs_3plus": blank_runs, "line_count": len(lines)}

def repetition_checks(text: str, window: int = 80) -> Dict[str, object]:
    words = [w.lower() for w in tokens(text)]
    total_words = len(words)

    # Immediate duplicates (the the)
    immediate_dups = []
    for i in range(len(words) - 1):
        if words[i] == words[i+1]:
            immediate_dups.append(words[i])

    # Overall top repeats (excluding common stopwords to focus on style tics)
    STOP = {
        "the","a","an","and","or","but","if","then","of","to","in","on","for","with","as",
        "at","by","from","that","this","it","is","was","were","be","been","are","i","you",
        "he","she","they","we","my","your","his","her","their","our","not","no","so"
    }
    counter = Counter([w for w in words if w not in STOP and len(w) > 2])
    top_overall = counter.most_common(20)

    # Sliding-window repeats: if a word appears >= N times within a window, flag it
    N = 6  # threshold occurrences per window
    flagged = Counter()
    dq = deque()
    counts = Counter()
    for i, w in enumerate(words):
        dq.append(w)
        counts[w] += 1
        if len(dq) > window:
            old = dq.popleft()
            counts[old] -= 1
            if counts[old] <= 0:
                del counts[old]
        # flag any words over threshold in current window
        for ww, c in list(counts.items()):
            if c >= N and ww not in STOP:
                flagged[ww] += 1  # rough: count how many windows where it exceeded threshold

    return {
        "immediate_duplicate_words": Counter(immediate_dups).most_common(),
        "top_repeated_words_overall": top_overall,
        "window_repetition_flags": flagged.most_common(20),
        "window_size": window,
        "threshold_per_window": N,
        "total_words": total_words,
    }

def unmatched_punctuation(text: str) -> Dict[str, int]:
    def balance(open_char: str, close_char: str) -> int:
        return text.count(open_char) - text.count(close_char)

    return {
        "paren_unmatched": balance("(", ")"),
        "bracket_unmatched": balance("[", "]"),
        "brace_unmatched": balance("{", "}"),
        "double_quote_unmatched": text.count('"') % 2,
        "single_quote_unmatched": text.count("'") % 2,
    }

# ---------------
# Normalizer
# ---------------
def normalize_plain(text: str) -> str:
    # Straight quotes, triple-dot ellipses, em dashes, collapse spaces
    t = normalize_newlines(text)
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("…", "...")
    # Convert spaced hyphen-as-dash to em dash
    t = re.sub(r"\s-\s", " — ", t)
    # collapse 3+ spaces to 1 (but preserve indentation at line start)
    def collapse_line(ln: str) -> str:
        if ln.startswith("    "):  # basic indentation preservation (4 spaces)
            prefix, rest = ln[:4], ln[4:]
            rest = re.sub(r" {2,}", " ", rest)
            return prefix + rest
        return re.sub(r" {2,}", " ", ln)
    t = "\n".join(collapse_line(ln) for ln in t.split("\n"))
    t = t.replace("\xa0", " ")
    t = re.sub(r"\t", "    ", t)
    return t

def normalize_smart(text: str) -> str:
    # Curly quotes, ellipsis char, em dash, tidy spacing
    t = normalize_plain(text)
    # Straight to curly (basic heuristic; doesn't handle edge cases like feet/inches perfectly)
    t = re.sub(r'"([^"]*)"', r'“\1”', t)
    t = re.sub(r"'([^']*)'", r'‘\1’', t)
    # Use unicode ellipsis
    t = t.replace("...", "…")
    # Trim spaces around em dashes to a single rule: no spaces
    t = re.sub(r"\s*—\s*", "—", t)
    return t

# ---------------
# Report dataclass
# ---------------
@dataclass
class MechanicsReport:
    total_words: int
    punctuation_overuse: Dict[str, Dict[str, float]]
    typography_issues: Dict[str, int]
    spacing_layout: Dict[str, int]
    repetition: Dict[str, object]
    unmatched_punctuation: Dict[str, int]

# ---------------
# Analysis
# ---------------
def analyze_mechanics(text: str) -> MechanicsReport:
    text_n = normalize_newlines(text)
    total_words = len(tokens(text_n))

    return MechanicsReport(
        total_words=total_words,
        punctuation_overuse=punctuation_overuse(text_n, total_words),
        typography_issues=typography_issues(text_n),
        spacing_layout=spacing_layout(text_n),
        repetition=repetition_checks(text_n),
        unmatched_punctuation=unmatched_punctuation(text_n),
    )

# ---------------
# CLI
# ---------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Mechanics & Cleanup analysis for a chapter (.txt).")
    parser.add_argument("input", type=str, help="Path to the chapter .txt file")
    parser.add_argument("--json", type=str, default="", help="Optional path to write JSON report")
    parser.add_argument("--write_normalized", type=str, default="", help="Optional path to write normalized text")
    parser.add_argument("--style", type=str, choices=["plain","smart"], default="plain", help="Normalization style (plain or smart)")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    text = in_path.read_text(encoding="utf-8", errors="ignore")
    report = analyze_mechanics(text)

    # Human-readable summary
    print("\n=== Mechanics & Cleanup Report ===")
    print(f"File: {in_path}")
    print(f"Total words: {report.total_words:,}\n")

    print("Punctuation overuse (per 1k words):")
    for k,v in report.punctuation_overuse.items():
        print(f"  - {k}: {v['count']} (density {v['per_1k_words']})")

    print("\nTypography issues:")
    for k,v in report.typography_issues.items():
        print(f"  - {k}: {v}")

    print("\nSpacing & layout:")
    for k,v in report.spacing_layout.items():
        print(f"  - {k}: {v}")

    print("\nRepetition:")
    print(f"  - immediate duplicate words: {report.repetition['immediate_duplicate_words'][:10]}")
    print(f"  - top repeated words overall: {report.repetition['top_repeated_words_overall'][:10]}")
    print(f"  - window repetition flags (window={report.repetition['window_size']}, threshold={report.repetition['threshold_per_window']}): {report.repetition['window_repetition_flags'][:10]}")

    print("\nUnmatched punctuation:")
    for k,v in report.unmatched_punctuation.items():
        print(f"  - {k}: {v}")

    # JSON output
    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out_path.resolve()}")

    # Optional normalized output
    if args.write_normalized:
        if args.style == "smart":
            fixed = normalize_smart(text)
        else:
            fixed = normalize_plain(text)
        out_norm = Path(args.write_normalized)
        out_norm.write_text(fixed, encoding="utf-8")
        print(f"Normalized text written to: {out_norm.resolve()}  (style={args.style})")

if __name__ == "__main__":
    main()
