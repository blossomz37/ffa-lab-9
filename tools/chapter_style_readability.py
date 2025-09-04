#!/usr/bin/env python3
"""
chapter_style_readability.py
----------------------------
Analyze a chapter's style and readability with editor-focused signals.

WHAT THIS SCRIPT DOES
- Readability scores: Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog
- Sentence variety: average length, distribution, very-short/very-long ratios
- Passive voice heuristic: "to be" + past participle patterns
- Adverbs in -ly: counts, top offenders
- Filter/Filler words: e.g., just, very, really, suddenly, seems, quite, rather...
- Weak/linking verbs: e.g., was/were/is/are/be/been/being, have/had, do/did, get/got...
- Nominalizations: words ending in -tion/-ment/-ance/-ence/-ity/-ness/-ship/-al

USAGE
    python3 chapter_style_readability.py path/to/chapter.txt --json out.json

REQUIRES
- Python 3.9+
- No external libraries

NOTES
- All heuristics are intentionally simple and fast—use as signals, not verdicts.
- Feed clean, plain-text manuscript chapters for best results.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median
from typing import List, Dict, Tuple

# -----------------------------
# Tokenization & Regex
# -----------------------------
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

# Syllable heuristic (very rough): count vowel groups as syllables, subtract patterns.
VOWEL_GROUPS_RE = re.compile(r"[aeiouyAEIOUY]+")

# Passive voice heuristic: forms of "to be" followed by an adverb (optional) and a past participle.
# Example matches: "was taken", "is being followed", "were quickly dismissed"
BE_FORMS = r"(?:am|is|are|was|were|be|been|being)"
ADVERB_OPT = r"(?:\s+\w+ly)?"
PAST_PART = r"(?:\s+\w+(?:ed|en))"
PASSIVE_RE = re.compile(rf"\b{BE_FORMS}{ADVERB_OPT}{PAST_PART}\b", re.IGNORECASE)

# Common "filter/filler" words (customize as you like).
FILTER_WORDS = {
    "just","very","really","suddenly","seems","seemed","quite","rather","somewhat","perhaps","maybe",
    "almost","nearly","basically","literally","honestly","actually","obviously","clearly","simply",
    "start","started","begin","began","try","tried","managed","able","seem","felt","feel","think","thought",
    "look","looked","appear","appeared","realize","realized","decide","decided","remember","remembered"
}

# Weak/linking verbs (often fine in moderation; we flag density).
WEAK_VERBS = {
    "am","is","are","was","were","be","been","being",
    "have","has","had","do","does","did",
    "get","gets","got","seem","seems","seemed","feel","feels","felt",
    "think","thinks","thought","know","knows","knew","look","looks","looked"
}

# Nominalization suffixes (signals nouny abstractions that can hide action).
NOMINAL_SUFFIXES = ("tion","sion","ment","ance","ence","ity","ness","ship","ality","ability","ibility","ism","ization","isation")


# -----------------------------
# Helpers
# -----------------------------
def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def split_sentences(text: str) -> List[str]:
    t = re.sub(r"\s+", " ", text.strip())
    if not t:
        return []
    parts = SENTENCE_SPLIT_RE.split(t)
    return [s.strip() for s in parts if s.strip()]


def word_tokens(text: str) -> List[str]:
    return WORD_RE.findall(text)


def count_syllables(word: str) -> int:
    """Very rough syllable estimator for English."""
    w = word.lower()
    if not w:
        return 0
    groups = VOWEL_GROUPS_RE.findall(w)
    syll = max(1, len(groups))

    # Common silent 'e' rule
    if w.endswith("e") and not w.endswith(("le","ye")) and syll > 1:
        syll -= 1

    # Fix a couple of common exceptions
    if w.endswith(("tion","sion")):
        syll += 0  # already vowel-group counted; often fine
    return syll


def flesch_reading_ease(total_words: int, total_sentences: int, total_syllables: int) -> float:
    # Flesch Reading Ease: higher is easier. 206.835 - 1.015*(W/S) - 84.6*(SYL/W)
    if total_sentences == 0 or total_words == 0:
        return 0.0
    return round(206.835 - 1.015*(total_words/total_sentences) - 84.6*(total_syllables/total_words), 2)


def flesch_kincaid_grade(total_words: int, total_sentences: int, total_syllables: int) -> float:
    # Flesch-Kincaid Grade Level: 0.39*(W/S) + 11.8*(SYL/W) - 15.59
    if total_sentences == 0 or total_words == 0:
        return 0.0
    return round(0.39*(total_words/total_sentences) + 11.8*(total_syllables/total_words) - 15.59, 2)


def gunning_fog_index(total_words: int, total_sentences: int, complex_word_count: int) -> float:
    # Gunning Fog: 0.4 * [(W/S) + 100*(complex_words/W)]
    if total_sentences == 0 or total_words == 0:
        return 0.0
    return round(0.4 * ((total_words/total_sentences) + 100.0*(complex_word_count/total_words)), 2)


def is_complex_word(word: str) -> bool:
    # Heuristic: 3+ syllables and not a proper noun (starts uppercase amid lowercase).
    return count_syllables(word) >= 3 and not (word[:1].isupper() and word[1:].islower())


def passive_hits(text: str) -> int:
    return len(PASSIVE_RE.findall(text))


def adverb_ly_list(words: List[str]) -> List[str]:
    return [w for w in words if len(w) > 2 and w.lower().endswith("ly")]


def nominalizations(words: List[str]) -> List[str]:
    lows = [w.lower() for w in words]
    return [w for w in lows if w.endswith(NOMINAL_SUFFIXES)]


# -----------------------------
# Data structure
# -----------------------------
from dataclasses import dataclass

@dataclass
class StyleReport:
    # Readability
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float
    total_words: int
    total_sentences: int
    total_syllables: int
    complex_words: int

    # Sentence variety
    avg_sentence_len_words: float
    median_sentence_len_words: float
    min_sentence_len_words: int
    max_sentence_len_words: int
    stdev_sentence_len_words: float
    very_short_ratio: float  # <= 7 words
    very_long_ratio: float   # >= 25 words

    # Passive voice
    passive_count: int
    passive_density_per_1k_words: float

    # Adverbs (-ly)
    adverb_ly_count: int
    adverb_ly_top10: List[Tuple[str,int]]
    adverb_ly_ratio: float  # per 100 words

    # Filter/Filler words
    filter_count: int
    filter_top10: List[Tuple[str,int]]
    filter_ratio: float  # per 100 words

    # Weak verbs
    weak_verb_count: int
    weak_verb_top10: List[Tuple[str,int]]
    weak_verb_ratio: float  # per 100 words

    # Nominalizations
    nominalization_count: int
    nominalization_top10: List[Tuple[str,int]]
    nominalization_ratio: float  # per 100 words


# -----------------------------
# Core analysis
# -----------------------------
def analyze_style(text: str) -> StyleReport:
    text = normalize_text(text)
    sentences = split_sentences(text)
    words = word_tokens(text)

    # Readability pieces
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(w) for w in words)
    complex_words = sum(1 for w in words if is_complex_word(w))

    fre = flesch_reading_ease(total_words, total_sentences, total_syllables)
    fkg = flesch_kincaid_grade(total_words, total_sentences, total_syllables)
    fog = gunning_fog_index(total_words, total_sentences, complex_words)

    # Sentence length stats
    lens = [len(word_tokens(s)) for s in sentences if s.strip()]
    if lens:
        avg_len = mean(lens)
        med_len = median(lens)
        min_len = min(lens)
        max_len = max(lens)
        stdev = (mean((x - avg_len) ** 2 for x in lens)) ** 0.5
        very_short_ratio = sum(1 for x in lens if x <= 7) / len(lens)
        very_long_ratio  = sum(1 for x in lens if x >= 25) / len(lens)
    else:
        avg_len = med_len = stdev = 0.0
        min_len = max_len = 0
        very_short_ratio = very_long_ratio = 0.0

    # Passive voice
    passive_count = passive_hits(text)
    passive_density = (passive_count / total_words * 1000) if total_words else 0.0

    # Adverbs in -ly
    adverbs = adverb_ly_list(words)
    adv_count = len(adverbs)
    adv_counter = Counter(w.lower() for w in adverbs)
    adv_top = adv_counter.most_common(10)
    adv_ratio = (adv_count / total_words * 100) if total_words else 0.0

    # Filter words
    low_words = [w.lower() for w in words]
    filter_counter = Counter([w for w in low_words if w in FILTER_WORDS])
    filter_count = sum(filter_counter.values())
    filter_top = filter_counter.most_common(10)
    filter_ratio = (filter_count / total_words * 100) if total_words else 0.0

    # Weak verbs
    weak_counter = Counter([w for w in low_words if w in WEAK_VERBS])
    weak_count = sum(weak_counter.values())
    weak_top = weak_counter.most_common(10)
    weak_ratio = (weak_count / total_words * 100) if total_words else 0.0

    # Nominalizations
    nom_list = nominalizations(words)
    nom_counter = Counter(nom_list)
    nom_count = sum(nom_counter.values())
    nom_top = nom_counter.most_common(10)
    nom_ratio = (nom_count / total_words * 100) if total_words else 0.0

    return StyleReport(
        flesch_reading_ease=round(fre,2),
        flesch_kincaid_grade=round(fkg,2),
        gunning_fog=round(fog,2),
        total_words=total_words,
        total_sentences=total_sentences,
        total_syllables=total_syllables,
        complex_words=complex_words,
        avg_sentence_len_words=round(avg_len,2),
        median_sentence_len_words=round(med_len,2),
        min_sentence_len_words=int(min_len),
        max_sentence_len_words=int(max_len),
        stdev_sentence_len_words=round(stdev,2),
        very_short_ratio=round(very_short_ratio,3),
        very_long_ratio=round(very_long_ratio,3),
        passive_count=int(passive_count),
        passive_density_per_1k_words=round(passive_density,2),
        adverb_ly_count=int(adv_count),
        adverb_ly_top10=adv_top,
        adverb_ly_ratio=round(adv_ratio,2),
        filter_count=int(filter_count),
        filter_top10=filter_top,
        filter_ratio=round(filter_ratio,2),
        weak_verb_count=int(weak_count),
        weak_verb_top10=weak_top,
        weak_verb_ratio=round(weak_ratio,2),
        nominalization_count=int(nom_count),
        nominalization_top10=nom_top,
        nominalization_ratio=round(nom_ratio,2),
    )


# -----------------------------
# CLI
# -----------------------------
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Style & Readability analysis for a chapter (.txt).")
    parser.add_argument("input", type=str, help="Path to the chapter .txt file")
    parser.add_argument("--json", type=str, default="", help="Optional path to write JSON report")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    text = in_path.read_text(encoding="utf-8", errors="ignore")
    report = analyze_style(text)

    # Human-readable summary
    print("\n=== Style & Readability Report ===")
    print(f"File: {in_path}")
    print(f"Words: {report.total_words:,} | Sentences: {report.total_sentences:,}")
    print(f"Flesch Reading Ease: {report.flesch_reading_ease} (higher=easier)")
    print(f"Flesch-Kincaid Grade: {report.flesch_kincaid_grade}")
    print(f"Gunning Fog Index: {report.gunning_fog}")
    print(f"Sentence length (words): avg {report.avg_sentence_len_words}, med {report.median_sentence_len_words}, "
          f"min {report.min_sentence_len_words}, max {report.max_sentence_len_words}, stdev {report.stdev_sentence_len_words}")
    print(f"Very short (<=7 words): {report.very_short_ratio*100:.1f}% | Very long (>=25 words): {report.very_long_ratio*100:.1f}%")
    print(f"Passive voice (heuristic): {report.passive_count} hits | density {report.passive_density_per_1k_words} per 1k words")
    print(f"-ly adverbs: {report.adverb_ly_count} ({report.adverb_ly_ratio:.2f} per 100 words) | top: {report.adverb_ly_top10}")
    print(f"Filter/Filler words: {report.filter_count} ({report.filter_ratio:.2f} per 100 words) | top: {report.filter_top10}")
    print(f"Weak/linking verbs: {report.weak_verb_count} ({report.weak_verb_ratio:.2f} per 100 words) | top: {report.weak_verb_top10}")
    print(f"Nominalizations: {report.nominalization_count} ({report.nominalization_ratio:.2f} per 100 words) | top: {report.nominalization_top10}")

    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
