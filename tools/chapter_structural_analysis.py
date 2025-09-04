#!/usr/bin/env python3
"""
chapter_structural_analysis.py
--------------------------------
Analyze a single chapter (.txt) for editor-relevant structural metrics.

WHAT THIS SCRIPT DOES
- Counts words, sentences, and paragraphs
- Estimates reading time (at ~250 words/min by default)
- Computes sentence length distribution and basic pacing heuristics
- Detects "scenes" by common dividers (***, ###, ---) or runs of blank lines
- Heuristic "hook/cliffhanger" score for the final sentence

USAGE (from a terminal/shell)
    python3 chapter_structural_analysis.py path/to/chapter.txt --wpm 250 --json out.json

REQUIRES
- Python 3.9+
- No external libraries (pure standard library)

NOTE
- This is a heuristic tool intended to give quick "editor-style" signals.
- For best results, feed it clean, plain-text chapter files (no HTML/DocX).

"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median
from typing import List, Dict, Tuple


# -----------------------------
# Utility Regular Expressions
# -----------------------------
# Basic sentence boundary detector (simple heuristic):
#   - Splits on ., !, ? followed by a space or end-of-line.
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

# Word tokens (letters, digits, apostrophes/hyphens within words).
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

# Common scene-break tokens used in manuscripts.
SCENE_DIVIDERS = {"***", "###", "---", "§§§", "* * *"}

# Strong "energetic" verbs for last-line hook heuristic (tiny starter list; expand as you like).
STRONG_VERBS = {
    "shatter", "fracture", "vanish", "plunge", "ignite", "explode", "collapse", "betray",
    "discover", "confess", "appear", "disappear", "scream", "bleed", "break", "slam", "pound",
    "crash", "kill", "die", "lie", "reveal", "admit", "threaten", "forbid", "refuse", "dare"
}

# Words that can signal unresolved tension at line-end.
TENSION_ENDERS = {"?", "—", "–", "-", "…", "..."}


@dataclass
class StructuralReport:
    # Top-level structural metrics editors care about
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_sentence_len_words: float
    median_sentence_len_words: float
    min_sentence_len_words: int
    max_sentence_len_words: int
    sentence_len_stdev_words: float
    estimated_read_time_min: float

    # Scene metrics
    scene_count: int
    avg_words_per_scene: float
    scene_boundaries: List[int]  # Paragraph indexes where a new scene starts

    # Pacing heuristics
    short_sentence_ratio: float  # % of sentences <= 7 words
    long_sentence_ratio: float   # % of sentences >= 25 words

    # Hook/Cliffhanger heuristic
    last_line_hook_score: float
    last_line: str


# -----------------------------
# Core Text Normalization
# -----------------------------
def normalize_text(text: str) -> str:
    """
    Normalize whitespace to make parsing more predictable.
    - Convert Windows CRLF to LF
    - Collapse mixed whitespace lines
    """
    # Replace CRLF and CR with LF so we have consistent newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Strip trailing spaces on lines (tidier paragraphs)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text


# -----------------------------
# Paragraph and Sentence Parsing
# -----------------------------
def split_paragraphs(text: str) -> List[str]:
    """
    Paragraphs are separated by one or more blank lines.
    This mirrors how many manuscripts are saved as plain text.
    """
    # Split on 2+ newlines to identify paragraph blocks
    raw_paragraphs = re.split(r'\n{2,}', text)
    # Trim whitespace and drop empty
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    return paragraphs


def split_sentences(paragraph: str) -> List[str]:
    """
    Split a paragraph into sentences using a simple regex heuristic.
    This won't be perfect (e.g., Mr., Dr., initials), but it's good enough
    for macro metrics used by developmental editors.
    """
    # First collapse internal newlines to spaces for cleaner splitting
    para = re.sub(r'\s+', ' ', paragraph).strip()
    if not para:
        return []
    # Split on the regex and strip whitespace
    candidates = SENTENCE_SPLIT_RE.split(para)
    sentences = [s.strip() for s in candidates if s.strip()]
    return sentences


def word_tokens(text: str) -> List[str]:
    """
    Tokenize words using a simple regex.
    This is intentionally lightweight and language-agnostic.
    """
    return WORD_RE.findall(text)


# -----------------------------
# Scene Segmentation
# -----------------------------
def detect_scene_boundaries(paragraphs: List[str]) -> List[int]:
    """
    Detect scene breaks by scanning paragraph text:
      - A paragraph that equals one of SCENE_DIVIDERS
      - OR a long run of blank lines (already collapsed by split_paragraphs)
    We mark the paragraph *after* a divider as a new scene start.
    """
    boundaries = [0]  # First scene starts at paragraph 0
    for i, p in enumerate(paragraphs):
        # If a paragraph is exactly a known divider, next paragraph (i+1) starts a new scene
        if p.strip() in SCENE_DIVIDERS:
            nxt = i + 1
            if nxt < len(paragraphs):
                boundaries.append(nxt)
    # Deduplicate and ensure sorted
    boundaries = sorted(set(boundaries))
    return boundaries


def scene_stats(paragraphs: List[str], boundaries: List[int]) -> Tuple[int, float]:
    """
    Compute scene count and average words per scene.
    """
    # Cut the paragraphs into scene chunks
    scene_chunks: List[List[str]] = []
    for idx, start in enumerate(boundaries):
        # End is the next boundary or the end of the paragraphs
        end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(paragraphs)
        scene_chunks.append(paragraphs[start:end])

    # Compute words per scene by joining paragraphs in each chunk
    words_per_scene = []
    for chunk in scene_chunks:
        text = " ".join(chunk)
        words_per_scene.append(len(word_tokens(text)))

    scene_count = len(scene_chunks)
    avg_words = mean(words_per_scene) if words_per_scene else 0.0
    return scene_count, avg_words


# -----------------------------
# Pacing and Hook Heuristics
# -----------------------------
def sentence_length_stats(sentences: List[str]) -> Dict[str, float]:
    """
    Compute sentence length statistics (in words).
    """
    lens = [len(word_tokens(s)) for s in sentences if s.strip()]
    if not lens:
        return dict(
            avg=0.0, med=0.0, min=0, max=0, stdev=0.0,
            short_ratio=0.0, long_ratio=0.0
        )
    avg_len = mean(lens)
    med_len = median(lens)
    min_len = min(lens)
    max_len = max(lens)
    # Simple standard deviation (population)
    stdev = (mean((x - avg_len) ** 2 for x in lens)) ** 0.5
    total = len(lens)
    short_ratio = sum(1 for x in lens if x <= 7) / total  # <= 7 words = "punchy"
    long_ratio = sum(1 for x in lens if x >= 25) / total  # >= 25 words = "long"
    return dict(
        avg=avg_len, med=med_len, min=min_len, max=max_len, stdev=stdev,
        short_ratio=short_ratio, long_ratio=long_ratio
    )


def estimate_read_time_min(word_count: int, wpm: int = 250) -> float:
    """
    Estimate reading time in minutes based on words-per-minute.
    250 WPM is a common estimate for general fiction.
    """
    if wpm <= 0:
        wpm = 250
    return round(word_count / wpm, 2)


def last_line_hook_score(last_sentence: str) -> float:
    """
    A playful heuristic to score the "hookiness" of the final sentence.
    Signals considered:
      - Ends with ?, —, …, or - (unresolved punctuation)
      - Contains strong/energetic verbs
      - Contains a direct threat or discovery lexeme (tiny list above)
    The score is 0–1.0. Tunable by increasing weights or keyword lists.
    """
    if not last_sentence:
        return 0.0

    s = last_sentence.strip()
    words = {w.lower() for w in word_tokens(s)}
    score = 0.0

    # Ending punctuation tension
    if s[-1:] in TENSION_ENDERS:
        score += 0.4

    # Strong verbs in the line
    strong_hits = len(words.intersection(STRONG_VERBS))
    if strong_hits > 0:
        # cap contribution at 0.4
        score += min(0.1 * strong_hits, 0.4)

    # Interrogative words at the start can add tension
    if s[:1] == "?" or re.match(r'^(who|what|why|how|where|when)\b', s.lower()):
        score += 0.2

    # Clamp to [0,1]
    return max(0.0, min(1.0, round(score, 2)))


# -----------------------------
# Main Analysis Function
# -----------------------------
def analyze_chapter(text: str, wpm: int = 250) -> StructuralReport:
    """
    Produce the StructuralReport dataclass for a given chapter text.
    """
    text = normalize_text(text)
    paragraphs = split_paragraphs(text)

    # Gather all sentences (flattened)
    all_sentences: List[str] = []
    for p in paragraphs:
        # Bypass scene divider paragraphs (they are not part of prose)
        if p.strip() in SCENE_DIVIDERS:
            continue
        all_sentences.extend(split_sentences(p))

    # Word and paragraph counts
    total_words = len(word_tokens(text))
    paragraph_count = len([p for p in paragraphs if p.strip() and p.strip() not in SCENE_DIVIDERS])

    # Sentence statistics
    s_stats = sentence_length_stats(all_sentences)
    estimated_min = estimate_read_time_min(total_words, wpm)

    # Scene detection and stats
    boundaries = detect_scene_boundaries(paragraphs)
    scene_count, avg_words_per_scene = scene_stats(paragraphs, boundaries)

    # Hook score on the final sentence (if present)
    last_line = all_sentences[-1] if all_sentences else ""
    hook_score = last_line_hook_score(last_line)

    report = StructuralReport(
        word_count=total_words,
        sentence_count=len(all_sentences),
        paragraph_count=paragraph_count,
        avg_sentence_len_words=round(s_stats["avg"], 2),
        median_sentence_len_words=round(s_stats["med"], 2),
        min_sentence_len_words=int(s_stats["min"]),
        max_sentence_len_words=int(s_stats["max"]),
        sentence_len_stdev_words=round(s_stats["stdev"], 2),
        estimated_read_time_min=estimated_min,
        scene_count=scene_count,
        avg_words_per_scene=round(avg_words_per_scene, 2),
        scene_boundaries=boundaries,
        short_sentence_ratio=round(s_stats["short_ratio"], 3),
        long_sentence_ratio=round(s_stats["long_ratio"], 3),
        last_line_hook_score=hook_score,
        last_line=last_line,
    )
    return report


# -----------------------------
# Command-Line Interface (CLI)
# -----------------------------
def main() -> None:
    # argparse gives your script a friendly command-line interface.
    parser = argparse.ArgumentParser(
        description="Analyze structural metrics of a chapter text file (editor-focused)."
    )
    parser.add_argument("input", type=str, help="Path to the chapter .txt file")
    parser.add_argument("--wpm", type=int, default=250, help="Words per minute for read-time estimate")
    parser.add_argument("--json", type=str, default="", help="Optional path to write JSON report")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    # Read the text file (UTF-8 by default)
    text = in_path.read_text(encoding="utf-8", errors="ignore")

    # Run analysis
    report = analyze_chapter(text, wpm=args.wpm)

    # Print a human-readable summary to stdout (your terminal)
    print("\n=== Structural Report ===")
    print(f"File: {in_path}")
    print(f"Words: {report.word_count:,} | Sentences: {report.sentence_count:,} | Paragraphs: {report.paragraph_count:,}")
    print(f"Estimated read time: {report.estimated_read_time_min} min (at {args.wpm} wpm)")
    print(f"Sentence length (words): avg {report.avg_sentence_len_words}, med {report.median_sentence_len_words}, "
          f"min {report.min_sentence_len_words}, max {report.max_sentence_len_words}, stdev {report.sentence_len_stdev_words}")
    print(f"Short sentence ratio (<=7 words): {report.short_sentence_ratio*100:.1f}% | "
          f"Long sentence ratio (>=25 words): {report.long_sentence_ratio*100:.1f}%")
    print(f"Scenes: {report.scene_count} | Avg words/scene: {report.avg_words_per_scene}")
    print(f"Scene boundaries (paragraph indexes): {report.scene_boundaries}")
    print(f"Last line hook score (0-1): {report.last_line_hook_score}")
    if report.last_line:
        print(f"Last line: {report.last_line}")

    # Optionally write the full JSON for downstream tools
    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
