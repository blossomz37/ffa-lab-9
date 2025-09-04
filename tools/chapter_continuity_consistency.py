#!/usr/bin/env python3
"""
chapter_continuity_consistency.py
---------------------------------
Continuity & consistency checks an editor cares about.

WHAT THIS SCRIPT DOES
- Name/term consistency:
    * Detects probable variants via fuzzy matching (difflib)
    * Supports a canon list (CSV/JSON) of names/terms with allowed aliases
- Hyphenation/style variants:
    * Flags pairs like "e-mail" vs "email", "co-operate" vs "cooperate"
- Time/place markers:
    * Finds weekdays, months, clock times, relative-day phrases, explicit dates
- Pronoun ambiguity heuristic:
    * Flags sentences heavy in pronouns without clear noun anchors
    * Detects long runs of pronoun-led sentences
- POV drift signals:
    * Counts 1st vs 2nd vs 3rd-person pronouns; flags mixed POV density
- Tense consistency (very rough):
    * Ratio of past-tense -ed verbs vs present-tense be/have/do forms
- Quote style consistency:
    * Counts straight vs curly quotes, mixed usage

USAGE
    python3 chapter_continuity_consistency.py path/to/chapter.txt \
        --canon_csv path/to/canon.csv \
        --canon_json path/to/canon.json \
        --names "Thea, Enid, Declan" \
        --json out.json

CANON FORMAT
- CSV: any cell is treated as a canonical name/term; duplicates allowed
- JSON: {"canon": [{"name": "Thea", "aliases": ["Theia"]}, {"name":"Blackwood Inn","aliases":["Blackwood Inn."]}]}

NOTES
- Heuristics are signals to investigate, not final judgments.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import difflib
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*")

def normalize_text(text: str) -> str:
    return (text.replace("\r\n","\n").replace("\r","\n"))

def word_tokens(s: str) -> List[str]:
    return WORD_RE.findall(s)

def sentences(text: str) -> List[str]:
    # Naive splitter on . ! ? followed by whitespace/newline
    parts = re.split(r'(?<=[.!?])\s+', re.sub(r'\s+',' ', text.strip()))
    return [p.strip() for p in parts if p.strip()]

def load_canon(csv_path: str, json_path: str, inline_names: str) -> Dict[str, Set[str]]:
    """
    Return mapping canonical -> set(aliases incl canonical).
    For CSV, each cell is its own canonical with no aliases (you can duplicate to simulate aliases).
    For JSON, use objects with "name" and optional "aliases".
    Inline names become canonical entries without aliases.
    """
    canon: Dict[str, Set[str]] = defaultdict(set)
    if csv_path:
        p = Path(csv_path)
        if p.exists():
            with p.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        nm = cell.strip()
                        if nm:
                            canon[nm].add(nm)
    if json_path:
        p = Path(json_path)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            for item in data.get("canon", []):
                name = item.get("name","").strip()
                if not name: 
                    continue
                canon[name].add(name)
                for alias in item.get("aliases", []):
                    a = alias.strip()
                    if a:
                        canon[name].add(a)
    if inline_names:
        for part in inline_names.split(","):
            nm = part.strip()
            if nm:
                canon[nm].add(nm)
    # Also add lowercase variants for lookups
    canon_norm = {k: set(list(v) + [x.lower() for x in v]) for k, v in canon.items()}
    return canon_norm

# -----------------------------
# Name/term consistency via fuzzy matching
# -----------------------------
def probable_variants(tokens: List[str], min_len: int = 3, cutoff: float = 0.88) -> List[Tuple[str,str,float]]:
    """
    Find pairs of tokens that are very similar (possible misspellings/variants).
    Uses difflib.SequenceMatcher ratio; returns pairs tokenA, tokenB, score.
    """
    # Only consider capitalized or multi-word-likes by later logic; here just filter by length.
    uniq = sorted({t for t in tokens if len(t) >= min_len})
    results: List[Tuple[str,str,float]] = []
    # Limit comparisons by grouping by first letter to keep it cheap
    buckets: Dict[str, List[str]] = defaultdict(list)
    for t in uniq:
        buckets[t[0].lower()].append(t)
    for bucket in buckets.values():
        for i in range(len(bucket)):
            for j in range(i+1, len(bucket)):
                a, b = bucket[i], bucket[j]
                # skip identical lowercased
                if a.lower() == b.lower():
                    continue
                score = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
                if score >= cutoff:
                    results.append((a, b, round(score, 3)))
    return results

# -----------------------------
# Hyphenation/style variants
# -----------------------------
def hyphenation_pairs(tokens: List[str]) -> List[Tuple[str,str]]:
    """
    Detect tokens that appear both hyphenated and unhyphenated, e.g., e-mail vs email.
    """
    lows = [t.lower() for t in tokens]
    s = set(lows)
    pairs = []
    for w in list(s):
        if "-" in w:
            un = w.replace("-", "")
            if un in s:
                pairs.append((w, un))
    return sorted(set(pairs))

# -----------------------------
# Time/place markers
# -----------------------------
WEEKDAYS = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday"}
MONTHS = {"january","february","march","april","may","june","july","august","september","october","november","december"}
REL_DAYS = {"yesterday","today","tonight","tomorrow","this morning","this afternoon","this evening","last night"}
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b|\b(?:[1-9]|1[0-2])\s?(?:am|pm|a\.m\.|p\.m\.)\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b")

def time_place_markers(text: str) -> Dict[str, List[str]]:
    lows = text.lower()
    found_weekdays = [w for w in WEEKDAYS if w in lows]
    found_months   = [m for m in MONTHS if m in lows]
    found_rel = []
    for phrase in REL_DAYS:
        if phrase in lows:
            found_rel.append(phrase)
    found_times = TIME_RE.findall(text)
    found_dates = DATE_RE.findall(text)
    return {
        "weekdays": sorted(found_weekdays),
        "months": sorted(found_months),
        "relative": sorted(found_rel),
        "times": found_times,
        "dates": found_dates,
    }

# -----------------------------
# Pronoun ambiguity
# -----------------------------
PRONOUNS = {"he","she","they","him","her","them","his","hers","theirs","it","its"}

def pronoun_ambiguity(sent_list: List[str]) -> Dict[str, int]:
    """
    Heuristic flags:
      - sentences with >=3 pronouns and no proper noun
      - longest run of consecutive pronoun-led sentences (starting with a pronoun)
    """
    ambiguous = 0
    max_run = 0
    cur_run = 0
    for s in sent_list:
        toks = word_tokens(s)
        lows = [t.lower() for t in toks]
        proper_noun_present = any(t[:1].isupper() for t in toks)
        pron_count = sum(1 for t in lows if t in PRONOUNS)

        if pron_count >= 3 and not proper_noun_present:
            ambiguous += 1

        # run of pronoun-led sentences
        if lows and lows[0] in PRONOUNS:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 0

    return {"ambiguous_sentences": ambiguous, "max_pronoun_led_run": max_run}

# -----------------------------
# POV & Tense signals
# -----------------------------
FIRST_PRON = {"i","me","my","mine","we","us","our","ours"}
SECOND_PRON = {"you","your","yours"}
THIRD_PRON = {"he","she","they","him","her","them","his","hers","theirs","it","its"}

BE_FORMS = {"am","is","are","was","were","be","been","being"}
HAVE_FORMS = {"have","has","had"}
DO_FORMS = {"do","does","did"}

def pov_and_tense(tokens: List[str]) -> Dict[str, float]:
    lows = [t.lower() for t in tokens]
    total = len(lows) or 1
    first = sum(1 for t in lows if t in FIRST_PRON) / total
    second = sum(1 for t in lows if t in SECOND_PRON) / total
    third = sum(1 for t in lows if t in THIRD_PRON) / total

    # Tense: very rough
    past_ed = sum(1 for t in lows if len(t) > 3 and t.endswith("ed"))
    present_be = sum(1 for t in lows if t in BE_FORMS)
    present_do_have = sum(1 for t in lows if t in HAVE_FORMS or t in DO_FORMS)
    return {
        "first_person_ratio": round(first,3),
        "second_person_ratio": round(second,3),
        "third_person_ratio": round(third,3),
        "past_ed_ratio": round(past_ed/total,3),
        "present_aux_ratio": round((present_be+present_do_have)/total,3),
    }

# -----------------------------
# Quote style consistency
# -----------------------------
def quote_style_counts(text: str) -> Dict[str,int]:
    straight = text.count('"') + text.count("'")
    curly = text.count("“") + text.count("”") + text.count("‘") + text.count("’")
    return {"straight_quotes": straight, "curly_quotes": curly}

# -----------------------------
# Report structure
# -----------------------------
@dataclass
class ContinuityReport:
    # Canon & name/term consistency
    canonical_matches: Dict[str, int]                 # canonical -> count
    canonical_alias_hits: Dict[str, Dict[str,int]]    # canonical -> alias -> count
    probable_variants: List[Tuple[str,str,float]]

    # Hyphenation/style
    hyphenation_pairs: List[Tuple[str,str]]

    # Time/place markers
    time_place_markers: Dict[str, List[str]]

    # Pronoun ambiguity
    ambiguous_sentences: int
    max_pronoun_led_run: int

    # POV/Tense
    first_person_ratio: float
    second_person_ratio: float
    third_person_ratio: float
    past_ed_ratio: float
    present_aux_ratio: float

    # Quote style
    quote_style: Dict[str,int]


# -----------------------------
# Core analysis
# -----------------------------
def analyze_continuity(text: str, canon: Dict[str, Set[str]]) -> ContinuityReport:
    text_n = normalize_text(text)
    toks = word_tokens(text_n)
    sents = sentences(text_n)

    # Canonical matching
    canonical_matches: Dict[str, int] = {}
    canonical_alias_hits: Dict[str, Dict[str,int]] = {}
    lows = [t.lower() for t in toks]

    if canon:
        for canon_name, aliases in canon.items():
            # Count occurrences for each alias (case-insensitive exact token match or whole-phrase find)
            alias_counts: Dict[str,int] = {}
            for a in aliases:
                if not a:
                    continue
                if " " in a.strip():
                    # phrase count
                    pattern = re.compile(rf"\b{re.escape(a)}\b", re.IGNORECASE)
                    alias_counts[a] = len(pattern.findall(text_n))
                else:
                    alias_counts[a] = lows.count(a.lower())
            total = sum(alias_counts.values())
            if total > 0:
                canonical_matches[canon_name] = total
                # keep only aliases that actually appeared
                canonical_alias_hits[canon_name] = {k:v for k,v in alias_counts.items() if v>0}

    # Probable variants (possible misspellings) among Proper Nouns & capitalized words
    proper_like = [t for t in toks if t[:1].isupper() and len(t) >= 3]
    prob_vars = probable_variants(proper_like, cutoff=0.9)

    # Hyphenation/style variants
    hyph_pairs = hyphenation_pairs(toks)

    # Time/place markers
    tp = time_place_markers(text_n)

    # Pronoun ambiguity
    pa = pronoun_ambiguity(sents)

    # POV/Tense
    pov = pov_and_tense(toks)

    # Quote style
    qs = quote_style_counts(text)

    return ContinuityReport(
        canonical_matches=canonical_matches,
        canonical_alias_hits=canonical_alias_hits,
        probable_variants=prob_vars,
        hyphenation_pairs=hyph_pairs,
        time_place_markers=tp,
        ambiguous_sentences=pa["ambiguous_sentences"],
        max_pronoun_led_run=pa["max_pronoun_led_run"],
        first_person_ratio=pov["first_person_ratio"],
        second_person_ratio=pov["second_person_ratio"],
        third_person_ratio=pov["third_person_ratio"],
        past_ed_ratio=pov["past_ed_ratio"],
        present_aux_ratio=pov["present_aux_ratio"],
        quote_style=qs,
    )


# -----------------------------
# CLI
# -----------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Continuity & Consistency analysis for a chapter (.txt).")
    parser.add_argument("input", type=str, help="Path to the chapter .txt file")
    parser.add_argument("--canon_csv", type=str, default="", help="CSV of canonical names/terms (aliases by repetition)")
    parser.add_argument("--canon_json", type=str, default="", help="JSON with {'canon':[{'name':..., 'aliases':[...]}]}")
    parser.add_argument("--names", type=str, default="", help="Inline comma-separated list of canonical names")
    parser.add_argument("--json", type=str, default="", help="Optional path to write JSON report")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    canon = load_canon(args.canon_csv, args.canon_json, args.names)

    text = in_path.read_text(encoding="utf-8", errors="ignore")
    report = analyze_continuity(text, canon)

    # Human-readable summary
    print("\n=== Continuity & Consistency Report ===")
    print(f"File: {in_path}")
    if report.canonical_matches:
        print("Canonical matches (total occurrences):")
        for k, v in report.canonical_matches.items():
            print(f"  - {k}: {v} (aliases seen: {list(report.canonical_alias_hits.get(k, {}).items())})")
    else:
        print("Canonical matches: (none provided or none found)")

    if report.probable_variants:
        print("Probable variants (possible misspellings):")
        for a,b,score in report.probable_variants[:20]:
            print(f"  - {a} ~ {b} (similarity {score})")
    else:
        print("Probable variants: (none detected at current threshold)")

    if report.hyphenation_pairs:
        print("Hyphenation/style pairs detected:")
        for a,b in report.hyphenation_pairs[:20]:
            print(f"  - {a}  <->  {b}")
    else:
        print("Hyphenation/style pairs: (none)")

    print("Time/Place markers:")
    for k, v in report.time_place_markers.items():
        print(f"  - {k}: {v}")

    print(f"Pronoun ambiguity — ambiguous sentences: {report.ambiguous_sentences} | max pronoun-led run: {report.max_pronoun_led_run}")
    print(f"POV ratios — 1st: {report.first_person_ratio}, 2nd: {report.second_person_ratio}, 3rd: {report.third_person_ratio}")
    print(f"Tense signals — past '-ed' ratio: {report.past_ed_ratio}, present aux ratio: {report.present_aux_ratio}")
    print(f"Quote style counts — straight: {report.quote_style['straight_quotes']}, curly: {report.quote_style['curly_quotes']}")

    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
