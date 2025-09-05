#!/usr/bin/env python3
"""
chapter_character_dialogue.py
-----------------------------
Analyze character & dialogue signals that editors care about.

WHAT THIS SCRIPT DOES
- Dialogue ratio: proportion of dialogue vs narration by tokens and by line count
- Dialogue line stats: avg words per spoken line, very short/very long line ratios
- Dialogue tag usage: counts of "said/asked" vs ornate tags ("exclaimed", "growled", etc.)
- Speaker heuristics:
    * Attribution from "[...]," Name said / said Name
    * Attribution from pronouns near dialogue (very rough fallback)
    * Optional: supply a list of known character names for better matching
- Character mentions: frequency of names across the chapter
- Dialogue punctuation signals: exclamation/ellipsis/question density inside quotes
- Overused beats: parentheses or em-dashes within dialogue (stage directions density)

USAGE
    python3 chapter_character_dialogue.py path/to/chapter.txt \
        --characters "Thea, Enid, Declan" \
        --names_csv path/to/names.csv \
        --json out.json

NOTES
- Heuristics are intentionally simple; they provide quick signals, not ground truth.
- Works best with standard double quotes ("). If you use curly quotes, normalization tries to help.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median
from typing import List, Dict, Tuple, Set

# --------------------------------
# Basic tokenization and utilities
# --------------------------------
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

def normalize_quotes(text: str) -> str:
    """Normalize curly quotes to straight quotes for easier parsing."""
    return (text.replace("“", '"').replace("”", '"')
                .replace("‘", "'").replace("’", "'")
                .replace("\r\n", "\n").replace("\r", "\n"))

def word_tokens(s: str) -> List[str]:
    return WORD_RE.findall(s)


# --------------------------------
# Dialogue extraction
# --------------------------------
# We consider dialogue as text enclosed in double quotes (").
# This regex captures pairs of quotes and the text between them, non-greedily.
DIALOGUE_SPAN_RE = re.compile(r'"(.*?)"', re.DOTALL)

# "Said-bookism" tag candidates to flag (you can expand this list).
ORNATE_TAGS = {
    "exclaimed","shouted","yelled","screamed","whispered","murmured","muttered","growled","snapped",
    "hissed","breathed","sighed","barked","croaked","purred","roared","laughed","chuckled","gasped",
    "moaned","whimpered","screeched","snarled","sneered"
}

# Neutral tags we typically tolerate.
NEUTRAL_TAGS = {"said","asked","replied","answered","added","called","told"}

# Simple patterns for attribution near dialogue.
# Examples:
#   "Hello," Thea said.    -> Name + said
#   "Hello," said Thea.    -> said + Name
#   "Hello," she said.     -> pronoun + said (weak attribution)
ATTRIB_AFTER_NAME_RE = re.compile(r'"\s*[^"]*"\s*,?\s*(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|answered|added|called|told)\b')
ATTRIB_BEFORE_NAME_RE = re.compile(r'"\s*[^"]*"\s*,?\s*(?:said|asked|replied|answered|added|called|told)\s+(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
ATTRIB_PRONOUN_RE     = re.compile(r'"\s*[^"]*"\s*,?\s*(?:he|she|they|ze|xe)\s+(?:said|asked|replied|answered|added|called|told)\b', re.IGNORECASE)

# Characters: we allow passing a set of known names to boost attribution confidence.
def load_character_names(inline_list: str, csv_path: str) -> Set[str]:
    names: Set[str] = set()
    if inline_list:
        for part in inline_list.split(","):
            name = part.strip()
            if name:
                names.add(name)
    if csv_path:
        p = Path(csv_path)
        if p.exists():
            with p.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        nm = cell.strip()
                        if nm:
                            names.add(nm)
    # Add lowercase aliases for matching, but keep originals too
    names |= {n.lower() for n in list(names)}
    return names


# --------------------------------
# Data structures
# --------------------------------
from dataclasses import dataclass

@dataclass
class DialogueReport:
    # Totals
    total_tokens: int
    dialogue_tokens: int
    narration_tokens: int
    dialogue_ratio_by_tokens: float

    total_dialogue_lines: int
    total_narration_lines: int
    dialogue_ratio_by_lines: float

    # Dialogue line length stats
    avg_words_per_dialogue_line: float
    median_words_per_dialogue_line: float
    min_words_per_dialogue_line: int
    max_words_per_dialogue_line: int
    very_short_dialogue_ratio: float  # <= 5 words
    very_long_dialogue_ratio: float   # >= 20 words

    # Tags
    neutral_tag_count: int
    ornate_tag_count: int
    neutral_top5: List[Tuple[str,int]]
    ornate_top5: List[Tuple[str,int]]

    # Attribution
    attributed_by_name: List[Tuple[str,int]]   # (Name, count)
    attributed_by_pronoun_count: int
    unattributed_dialogue_lines: int

    # Character mentions (overall, not just in dialogue)
    character_mentions_top10: List[Tuple[str,int]]

    # Punctuation & beats inside dialogue
    question_mark_ratio_in_dialogue: float   # per 100 dialogue lines
    exclamation_ratio_in_dialogue: float     # per 100 dialogue lines
    ellipsis_ratio_in_dialogue: float        # per 100 dialogue lines
    emdash_ratio_in_dialogue: float          # per 100 dialogue lines
    parenthetical_ratio_in_dialogue: float   # per 100 dialogue lines
    

# --------------------------------
# Core analysis
# --------------------------------
def analyze_character_dialogue(text: str, known_names: Set[str]) -> DialogueReport:
    text = normalize_quotes(text)

    # Split text into lines to approximate "beats"; count dialogue vs narration lines.
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    total_tokens = len(word_tokens(text))

    # Extract dialogue spans
    spans = DIALOGUE_SPAN_RE.findall(text)
    dialogue_text = " ".join(spans)
    narration_text = DIALOGUE_SPAN_RE.sub(" ", text)  # remove dialogue, keep narration

    dialogue_tokens = len(word_tokens(dialogue_text))
    narration_tokens = max(0, total_tokens - dialogue_tokens)
    total_dialogue_lines = len(spans)
    total_narration_lines = max(0, len(lines) - total_dialogue_lines)

    ratio_by_tokens = (dialogue_tokens / total_tokens) if total_tokens else 0.0
    ratio_by_lines = (total_dialogue_lines / len(lines)) if lines else 0.0

    # Dialogue line length stats
    dialogue_line_lens = [len(word_tokens(s)) for s in spans if s.strip()]
    if dialogue_line_lens:
        avg_len = mean(dialogue_line_lens)
        med_len = median(dialogue_line_lens)
        min_len = min(dialogue_line_lens)
        max_len = max(dialogue_line_lens)
        very_short_ratio = sum(1 for x in dialogue_line_lens if x <= 5) / len(dialogue_line_lens)
        very_long_ratio  = sum(1 for x in dialogue_line_lens if x >= 20) / len(dialogue_line_lens)
    else:
        avg_len = med_len = 0.0
        min_len = max_len = 0
        very_short_ratio = very_long_ratio = 0.0

    # Tag usage
    # Strategy: scan narration immediately around each dialogue span for "said/asked/etc."
    neutral_counter = Counter()
    ornate_counter = Counter()

    # Build a simple iterator that gives context around each match
    tag_context_window = 80  # chars to the right of the closing quote
    for m in DIALOGUE_SPAN_RE.finditer(text):
        end = m.end()
        ctx = text[end:end+tag_context_window]  # characters after dialogue
        # Tokenize words in context to find tags
        ctx_words = [w.lower() for w in word_tokens(ctx)]
        for w in ctx_words[:6]:  # only look at first few words after dialogue
            if w in NEUTRAL_TAGS:
                neutral_counter[w] += 1
            elif w in ORNATE_TAGS:
                ornate_counter[w] += 1

    # Attribution heuristics (count by specific names if provided)
    name_attrib_counter = Counter()

    # Use regexes to find explicit "Name said" or "said Name" constructions
    for pat in (ATTRIB_AFTER_NAME_RE, ATTRIB_BEFORE_NAME_RE):
        for m in pat.finditer(text):
            name = m.group(1).strip()
            # If a known names list is provided, prefer only those; else accept any Capitalized phrase
            if known_names:
                if name in known_names or name.lower() in known_names:
                    name_attrib_counter[name] += 1
            else:
                name_attrib_counter[name] += 1

    pronoun_attrib_count = len(ATTRIB_PRONOUN_RE.findall(text))

    # Unattributed dialogue lines: total lines minus ones we saw attribution for (very rough)
    attributed_lines_est = sum(name_attrib_counter.values()) + pronoun_attrib_count
    unattributed = max(0, total_dialogue_lines - attributed_lines_est)

    # Character mentions overal (not just attributions). If known names provided, count those exactly;
    # otherwise approximate by counting capitalized tokens that are not sentence-initial "The", etc.
    character_mentions = Counter()
    tokens = word_tokens(text)
    lower_tokens = [t.lower() for t in tokens]
    if known_names:
        for nm in known_names:
            if len(nm) < 2: 
                continue
            # Count full-name and single-token occurrences
            if " " in nm:
                # naive whole-phrase count via regex
                pattern = re.compile(rf"\b{re.escape(nm)}\b", re.IGNORECASE)
                character_mentions[nm] += len(pattern.findall(text))
            else:
                character_mentions[nm] += lower_tokens.count(nm.lower())
    else:
        # naive proper-noun heuristic: capitalized tokens (skip common stop-words)
        STOP = {"The","A","An","I","He","She","They","We","It","His","Her","Hers","Their","Our","You"}
        for t in tokens:
            if t[:1].isupper() and t not in STOP and len(t) > 2:
                character_mentions[t] += 1

    # Punctuation & beats inside dialogue
    q = ex = ell = em = paren = 0
    for s in spans:
        if "?" in s: q += 1
        if "!" in s: ex += 1
        if "..." in s or "…" in s: ell += 1
        if "—" in s or "–" in s or " - " in s: em += 1
        if "(" in s or ")" in s: paren += 1

    def per_100_lines(x: int) -> float:
        return round((x / total_dialogue_lines * 100), 2) if total_dialogue_lines else 0.0

    report = DialogueReport(
        total_tokens=total_tokens,
        dialogue_tokens=dialogue_tokens,
        narration_tokens=narration_tokens,
        dialogue_ratio_by_tokens=round(ratio_by_tokens, 3),
        total_dialogue_lines=total_dialogue_lines,
        total_narration_lines=total_narration_lines,
        dialogue_ratio_by_lines=round(ratio_by_lines, 3),
        avg_words_per_dialogue_line=round(avg_len,2),
        median_words_per_dialogue_line=round(med_len,2),
        min_words_per_dialogue_line=int(min_len),
        max_words_per_dialogue_line=int(max_len),
        very_short_dialogue_ratio=round(very_short_ratio,3),
        very_long_dialogue_ratio=round(very_long_ratio,3),
        neutral_tag_count=sum(neutral_counter.values()),
        ornate_tag_count=sum(ornate_counter.values()),
        neutral_top5=neutral_counter.most_common(5),
        ornate_top5=ornate_counter.most_common(5),
        attributed_by_name=name_attrib_counter.most_common(10),
        attributed_by_pronoun_count=pronoun_attrib_count,
        unattributed_dialogue_lines=unattributed,
        character_mentions_top10=Counter(character_mentions).most_common(10),
        question_mark_ratio_in_dialogue=per_100_lines(q),
        exclamation_ratio_in_dialogue=per_100_lines(ex),
        ellipsis_ratio_in_dialogue=per_100_lines(ell),
        emdash_ratio_in_dialogue=per_100_lines(em),
        parenthetical_ratio_in_dialogue=per_100_lines(paren),
    )
    return report


# --------------------------------
# CLI
# --------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Character & Dialogue analysis for a chapter (.txt).")
    parser.add_argument("input", type=str, help="Path to the chapter .txt file")
    parser.add_argument("--characters", type=str, default="", help="Comma-separated character names")
    parser.add_argument("--names_csv", type=str, default="", help="CSV file of character names (any column)")
    parser.add_argument("--json", type=str, default="", help="Optional path to write JSON report")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    known = load_character_names(args.characters, args.names_csv)

    text = in_path.read_text(encoding="utf-8", errors="ignore")
    report = analyze_character_dialogue(text, known)

    # Human-readable summary
    print("\n=== Character & Dialogue Report ===")
    print(f"File: {in_path}")
    print(f"Dialogue ratio (tokens): {report.dialogue_ratio_by_tokens*100:.1f}%")
    print(f"Dialogue ratio (lines):  {report.dialogue_ratio_by_lines*100:.1f}%")
    print(f"Dialogue lines: {report.total_dialogue_lines} | Narration lines: {report.total_narration_lines}")
    print(f"Dialogue line length (words): avg {report.avg_words_per_dialogue_line}, med {report.median_words_per_dialogue_line}, "
          f"min {report.min_words_per_dialogue_line}, max {report.max_words_per_dialogue_line}")
    print(f"Very short (<=5): {report.very_short_dialogue_ratio*100:.1f}% | Very long (>=20): {report.very_long_dialogue_ratio*100:.1f}%")
    print(f"Tags — neutral: {report.neutral_tag_count} top {report.neutral_top5} | ornate: {report.ornate_tag_count} top {report.ornate_top5}")
    print(f"Attribution — by name: {report.attributed_by_name} | by pronoun: {report.attributed_by_pronoun_count} | unattributed lines (est): {report.unattributed_dialogue_lines}")
    print(f"Character mentions (top10): {report.character_mentions_top10}")
    print(f"In-dialogue punctuation per 100 lines — ? {report.question_mark_ratio_in_dialogue}, ! {report.exclamation_ratio_in_dialogue}, "
          f"... {report.ellipsis_ratio_in_dialogue}, — {report.emdash_ratio_in_dialogue}, () {report.parenthetical_ratio_in_dialogue}")

    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
