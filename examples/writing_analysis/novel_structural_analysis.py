#!/usr/bin/env python3
"""
novel_structural_analysis.py
----------------------------
Analyze a complete novel for comprehensive structural metrics using spaCy NLP.

WHAT THIS SCRIPT DOES
- Detects and counts acts, chapters, scenes, paragraphs, sentences, and words
- Uses spaCy for advanced linguistic analysis (POS tagging, NER, sentiment)
- Provides character analysis and dialogue detection
- Analyzes pacing and tension throughout the novel
- Generates detailed reports for developmental editors

USAGE (from a terminal/shell)
    python3 novel_structural_analysis.py path/to/novel.txt --output report.json --html report.html

REQUIRES
- Python 3.9+
- spaCy with medium English model: pip install spacy && python -m spacy download en_core_web_md
- Optional: matplotlib for visualizations

NOTE
- Expects well-formatted plain text with clear chapter/act divisions
- For best results, use consistent formatting for chapter headers
- Processing time: ~30 seconds to several minutes depending on novel length

"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median, stdev
from typing import List, Dict, Tuple, Optional, Set

try:
    import spacy
    from spacy.lang.en import English
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    print("Warning: spaCy not installed. Install with: pip install spacy && python -m spacy download en_core_web_md")

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# -----------------------------
# Text Structure Detection Patterns
# -----------------------------
# Chapter patterns (case-insensitive)
CHAPTER_PATTERNS = [
    r'^chapter\s+\d+',
    r'^ch\.\s*\d+',
    r'^\d+\.\s*',
    r'^part\s+\d+',
    r'^section\s+\d+'
]

# Act patterns (for plays or three-act novels)
ACT_PATTERNS = [
    r'^act\s+[ivxlc]+',
    r'^act\s+\d+',
    r'^book\s+\d+',
    r'^volume\s+\d+'
]

# Scene dividers
SCENE_DIVIDERS = {"***", "###", "---", "§§§", "* * *", "◊ ◊ ◊"}

# Advanced tension and emotion keywords for spaCy enhancement
TENSION_WORDS = {
    "high": {"crisis", "climax", "confrontation", "battle", "death", "murder", "explosion", "crash"},
    "medium": {"argument", "conflict", "tension", "worry", "fear", "anger", "surprise"},
    "low": {"calm", "peace", "quiet", "rest", "gentle", "soft", "comfort"}
}

EMOTION_WORDS = {
    "positive": {"joy", "love", "happiness", "delight", "pleasure", "satisfaction", "hope"},
    "negative": {"sadness", "grief", "despair", "hatred", "anger", "fear", "terror", "dread"},
    "neutral": {"confusion", "curiosity", "wonder", "interest", "focus", "attention"}
}


@dataclass
class CharacterMention:
    name: str
    count: int
    first_appearance: int  # Sentence index
    last_appearance: int
    chapters_present: Set[int]


@dataclass
class SceneAnalysis:
    start_paragraph: int
    end_paragraph: int
    word_count: int
    sentence_count: int
    character_mentions: Dict[str, int]
    dialogue_ratio: float
    tension_score: float
    emotion_score: float
    key_entities: List[str]


@dataclass
class ChapterAnalysis:
    chapter_number: int
    title: str
    start_paragraph: int
    end_paragraph: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    scene_count: int
    scenes: List[SceneAnalysis]
    avg_sentence_length: float
    dialogue_ratio: float
    character_mentions: Dict[str, int]
    tension_progression: List[float]
    readability_score: float
    hook_score: float
    cliffhanger_score: float


@dataclass
class ActAnalysis:
    act_number: int
    title: str
    start_chapter: int
    end_chapter: int
    chapters: List[ChapterAnalysis]
    total_words: int
    character_development: Dict[str, float]
    plot_progression: float


@dataclass
class NovelReport:
    # High-level structure
    title: str
    total_words: int
    total_sentences: int
    total_paragraphs: int
    act_count: int
    chapter_count: int
    scene_count: int
    
    # Timing and pacing
    estimated_read_time_hours: float
    avg_chapter_length: float
    avg_scene_length: float
    
    # Character analysis
    main_characters: Dict[str, CharacterMention]
    character_arc_analysis: Dict[str, Dict[str, float]]
    
    # Linguistic analysis
    avg_sentence_length: float
    vocabulary_richness: float
    dialogue_percentage: float
    
    # Structural analysis
    acts: List[ActAnalysis]
    pacing_analysis: Dict[str, float]
    tension_arc: List[float]
    
    # Advanced metrics
    genre_indicators: Dict[str, float]
    writing_style_metrics: Dict[str, float]
    consistency_scores: Dict[str, float]


class NovelAnalyzer:
    def __init__(self, model_name: str = "en_core_web_md"):
        if not HAS_SPACY:
            raise ImportError("spaCy is required. Install with: pip install spacy && python -m spacy download en_core_web_md")
        
        try:
            self.nlp = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name}")
        except OSError:
            print(f"Model {model_name} not found. Attempting to download...")
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
        
        # Optimize for longer texts
        self.nlp.max_length = 2000000  # Handle up to 2M characters
        
        # Add custom components for literary analysis
        self._add_custom_components()
    
    def _add_custom_components(self):
        """Add custom pipeline components for literary analysis."""
        
        @self.nlp.component("dialogue_detector")
        def dialogue_detector(doc):
            """Detect dialogue in text."""
            dialogue_markers = ['"', "'", '"', '"', ''', ''']
            for token in doc:
                if token.text in dialogue_markers:
                    token._.is_dialogue_marker = True
                else:
                    token._.is_dialogue_marker = False
            return doc
        
        # Register custom attributes
        if HAS_SPACY:
            spacy.tokens.Token.set_extension("is_dialogue_marker", default=False, force=True)
            spacy.tokens.Span.set_extension("tension_score", default=0.0, force=True)
            spacy.tokens.Span.set_extension("emotion_score", default=0.0, force=True)
        
        # Add the component to the pipeline
        if "dialogue_detector" not in self.nlp.pipe_names:
            self.nlp.add_pipe("dialogue_detector", last=True)
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent processing."""
        # Handle different line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Clean up excessive whitespace while preserving paragraph structure
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines)
    
    def detect_structure(self, text: str) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]], List[int]]:
        """Detect acts, chapters, and scenes in the text."""
        lines = text.split('\n')
        
        acts = []
        chapters = []
        scenes = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            
            # Check for acts
            for pattern in ACT_PATTERNS:
                if re.match(pattern, line_clean):
                    acts.append((i, line.strip()))
                    break
            
            # Check for chapters
            for pattern in CHAPTER_PATTERNS:
                if re.match(pattern, line_clean):
                    chapters.append((i, line.strip()))
                    break
            
            # Check for scene dividers
            if line.strip() in SCENE_DIVIDERS:
                scenes.append(i)
        
        return acts, chapters, scenes
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split on double newlines or more
        paragraphs = re.split(r'\n{2,}', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def calculate_dialogue_ratio(self, doc) -> float:
        """Calculate the ratio of dialogue to total text."""
        total_tokens = len(doc)
        if total_tokens == 0:
            return 0.0
        
        dialogue_tokens = 0
        in_dialogue = False
        
        for token in doc:
            if token._.is_dialogue_marker:
                in_dialogue = not in_dialogue
            elif in_dialogue:
                dialogue_tokens += 1
        
        return dialogue_tokens / total_tokens
    
    def calculate_tension_score(self, doc) -> float:
        """Calculate tension score based on word choice and sentence structure."""
        tension_score = 0.0
        total_words = len([token for token in doc if token.is_alpha])
        
        if total_words == 0:
            return 0.0
        
        for token in doc:
            word = token.lemma_.lower()
            if word in TENSION_WORDS["high"]:
                tension_score += 3
            elif word in TENSION_WORDS["medium"]:
                tension_score += 2
            elif word in TENSION_WORDS["low"]:
                tension_score -= 1
        
        # Normalize to 0-1 scale
        normalized_score = max(0, min(1, tension_score / total_words * 10))
        return round(normalized_score, 3)
    
    def calculate_emotion_score(self, doc) -> float:
        """Calculate overall emotional valence of the text."""
        emotion_score = 0.0
        total_words = len([token for token in doc if token.is_alpha])
        
        if total_words == 0:
            return 0.0
        
        for token in doc:
            word = token.lemma_.lower()
            if word in EMOTION_WORDS["positive"]:
                emotion_score += 1
            elif word in EMOTION_WORDS["negative"]:
                emotion_score -= 1
        
        # Normalize to -1 to 1 scale
        normalized_score = max(-1, min(1, emotion_score / total_words * 20))
        return round(normalized_score, 3)
    
    def extract_characters(self, doc) -> Dict[str, int]:
        """Extract character names using NER."""
        characters = Counter()
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Clean up the name
                name = ent.text.strip()
                if len(name) > 1 and name.isalpha():
                    characters[name] += 1
        
        return dict(characters)
    
    def analyze_scene(self, text: str, start_para: int, end_para: int) -> SceneAnalysis:
        """Analyze a single scene."""
        doc = self.nlp(text)
        
        # Basic counts
        sentences = list(doc.sents)
        words = [token for token in doc if token.is_alpha]
        
        # Advanced analysis
        dialogue_ratio = self.calculate_dialogue_ratio(doc)
        tension_score = self.calculate_tension_score(doc)
        emotion_score = self.calculate_emotion_score(doc)
        characters = self.extract_characters(doc)
        
        # Extract key entities
        key_entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "GPE", "ORG"]]
        
        return SceneAnalysis(
            start_paragraph=start_para,
            end_paragraph=end_para,
            word_count=len(words),
            sentence_count=len(sentences),
            character_mentions=characters,
            dialogue_ratio=dialogue_ratio,
            tension_score=tension_score,
            emotion_score=emotion_score,
            key_entities=key_entities[:10]  # Top 10 entities
        )
    
    def analyze_chapter(self, text: str, chapter_num: int, title: str, 
                       start_para: int, end_para: int, scene_boundaries: List[int]) -> ChapterAnalysis:
        """Analyze a single chapter."""
        doc = self.nlp(text)
        
        # Basic metrics
        sentences = list(doc.sents)
        words = [token for token in doc if token.is_alpha]
        paragraphs = self.split_into_paragraphs(text)
        
        avg_sent_len = mean([len([t for t in sent if t.is_alpha]) for sent in sentences]) if sentences else 0
        dialogue_ratio = self.calculate_dialogue_ratio(doc)
        characters = self.extract_characters(doc)
        
        # Analyze scenes within chapter
        scenes = []
        chapter_scene_boundaries = [b for b in scene_boundaries if start_para <= b <= end_para]
        
        for i, scene_start in enumerate(chapter_scene_boundaries):
            scene_end = (chapter_scene_boundaries[i + 1] if i + 1 < len(chapter_scene_boundaries) 
                        else end_para)
            scene_text = " ".join(paragraphs[scene_start:scene_end])
            if scene_text.strip():
                scene = self.analyze_scene(scene_text, scene_start, scene_end)
                scenes.append(scene)
        
        # Calculate tension progression (split chapter into 10 segments)
        tension_progression = []
        chunk_size = max(1, len(text) // 10)
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunk_doc = self.nlp(chunk[:100000])  # Limit chunk size for processing
                tension_progression.append(self.calculate_tension_score(chunk_doc))
        
        # Calculate hook and cliffhanger scores
        first_sent = sentences[0] if sentences else None
        last_sent = sentences[-1] if sentences else None
        
        hook_score = self._calculate_hook_score(first_sent) if first_sent else 0.0
        cliffhanger_score = self._calculate_cliffhanger_score(last_sent) if last_sent else 0.0
        
        return ChapterAnalysis(
            chapter_number=chapter_num,
            title=title,
            start_paragraph=start_para,
            end_paragraph=end_para,
            word_count=len(words),
            sentence_count=len(sentences),
            paragraph_count=len(paragraphs),
            scene_count=len(scenes),
            scenes=scenes,
            avg_sentence_length=round(avg_sent_len, 2),
            dialogue_ratio=round(dialogue_ratio, 3),
            character_mentions=characters,
            tension_progression=tension_progression,
            readability_score=self._calculate_readability(doc),
            hook_score=hook_score,
            cliffhanger_score=cliffhanger_score
        )
    
    def _calculate_hook_score(self, sentence) -> float:
        """Calculate how engaging the opening sentence is."""
        # This is a simplified heuristic - could be expanded
        tension_score = self.calculate_tension_score(sentence.as_doc())
        
        # Check for questions, dialogue, action
        text = sentence.text.strip()
        score = tension_score
        
        if text.endswith('?'):
            score += 0.3
        if text.startswith('"') or text.startswith('"'):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_cliffhanger_score(self, sentence) -> float:
        """Calculate how much suspense the ending sentence creates."""
        tension_score = self.calculate_tension_score(sentence.as_doc())
        
        text = sentence.text.strip()
        score = tension_score
        
        # Look for cliffhanger indicators
        if any(text.endswith(punct) for punct in ['?', '—', '…', '...']):
            score += 0.4
        if any(word in text.lower() for word in ['but', 'however', 'suddenly', 'then']):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_readability(self, doc) -> float:
        """Calculate a simple readability score."""
        sentences = list(doc.sents)
        words = [token for token in doc if token.is_alpha]
        
        if not sentences or not words:
            return 0.0
        
        avg_sent_length = len(words) / len(sentences)
        
        # Simple readability based on sentence length (inverse relationship)
        # Normalize to 0-1 scale where 1 is most readable
        readability = max(0, min(1, 1 - (avg_sent_length - 15) / 20))
        return round(readability, 3)
    
    def analyze_novel(self, text: str, title: str = "Unknown Novel") -> NovelReport:
        """Analyze the complete novel."""
        print(f"Starting analysis of '{title}'...")
        start_time = time.time()
        
        # Normalize text
        text = self.normalize_text(text)
        paragraphs = self.split_into_paragraphs(text)
        
        # Detect structure
        acts, chapters, scene_boundaries = self.detect_structure(text)
        
        print(f"Detected: {len(acts)} acts, {len(chapters)} chapters, {len(scene_boundaries)} scenes")
        
        # Process full text for global metrics
        print("Processing full text...")
        doc = self.nlp(text[:1000000])  # Limit for memory efficiency
        
        # Basic counts
        total_sentences = len(list(doc.sents))
        total_words = len([token for token in doc if token.is_alpha])
        
        # Character analysis
        all_characters = self.extract_characters(doc)
        # Convert to Counter for most_common method
        char_counter = Counter(all_characters)
        main_characters = {name: CharacterMention(
            name=name,
            count=count,
            first_appearance=0,  # Would need more detailed tracking
            last_appearance=total_sentences,
            chapters_present=set()
        ) for name, count in char_counter.most_common(10)}
        
        # Analyze chapters
        chapter_analyses = []
        if chapters:
            for i, (line_num, chapter_title) in enumerate(chapters):
                start_para = line_num
                end_para = chapters[i + 1][0] if i + 1 < len(chapters) else len(paragraphs)
                
                chapter_text = " ".join(paragraphs[start_para:end_para])
                if chapter_text.strip():
                    chapter_analysis = self.analyze_chapter(
                        chapter_text, i + 1, chapter_title, start_para, end_para, scene_boundaries
                    )
                    chapter_analyses.append(chapter_analysis)
        
        # Calculate advanced metrics
        avg_chapter_length = mean([ch.word_count for ch in chapter_analyses]) if chapter_analyses else 0
        avg_scene_length = total_words / len(scene_boundaries) if scene_boundaries else total_words
        
        # Estimate reading time (250 words per minute)
        read_time_hours = total_words / (250 * 60)
        
        # Overall dialogue percentage
        dialogue_percentage = self.calculate_dialogue_ratio(doc)
        
        # Tension arc (simplified)
        tension_arc = []
        if chapter_analyses:
            for chapter in chapter_analyses:
                if chapter.tension_progression:
                    tension_arc.extend(chapter.tension_progression)
        
        # Calculate vocabulary richness (type-token ratio)
        unique_words = len(set(token.lemma_.lower() for token in doc if token.is_alpha))
        vocab_richness = unique_words / total_words if total_words > 0 else 0
        
        elapsed_time = time.time() - start_time
        print(f"Analysis complete in {elapsed_time:.2f} seconds")
        
        return NovelReport(
            title=title,
            total_words=total_words,
            total_sentences=total_sentences,
            total_paragraphs=len(paragraphs),
            act_count=len(acts),
            chapter_count=len(chapters),
            scene_count=len(scene_boundaries),
            estimated_read_time_hours=round(read_time_hours, 2),
            avg_chapter_length=round(avg_chapter_length, 0),
            avg_scene_length=round(avg_scene_length, 0),
            main_characters=main_characters,
            character_arc_analysis={},  # Would need more sophisticated analysis
            avg_sentence_length=round(total_words / total_sentences if total_sentences > 0 else 0, 2),
            vocabulary_richness=round(vocab_richness, 3),
            dialogue_percentage=round(dialogue_percentage, 3),
            acts=[],  # Would need act-level analysis
            pacing_analysis={
                "overall_pace": mean(tension_arc) if tension_arc else 0.0,
                "pace_variation": stdev(tension_arc) if len(tension_arc) > 1 else 0.0
            },
            tension_arc=tension_arc,
            genre_indicators={},  # Could be expanded
            writing_style_metrics={
                "avg_sentence_length": round(total_words / total_sentences if total_sentences > 0 else 0, 2),
                "dialogue_ratio": round(dialogue_percentage, 3),
                "vocabulary_richness": round(vocab_richness, 3)
            },
            consistency_scores={}  # Could be expanded
        )


def generate_html_report(report: NovelReport, output_path: Path):
    """Generate an HTML report of the analysis."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Novel Analysis Report: {report.title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .metric {{ margin: 10px 0; }}
            .section {{ margin: 30px 0; border-left: 3px solid #007acc; padding-left: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Novel Analysis Report</h1>
            <h2>{report.title}</h2>
        </div>
        
        <div class="section">
            <h3>Overall Structure</h3>
            <div class="metric">Total Words: {report.total_words:,}</div>
            <div class="metric">Total Sentences: {report.total_sentences:,}</div>
            <div class="metric">Total Paragraphs: {report.total_paragraphs:,}</div>
            <div class="metric">Acts: {report.act_count}</div>
            <div class="metric">Chapters: {report.chapter_count}</div>
            <div class="metric">Scenes: {report.scene_count}</div>
            <div class="metric">Estimated Reading Time: {report.estimated_read_time_hours:.1f} hours</div>
        </div>
        
        <div class="section">
            <h3>Writing Style Metrics</h3>
            <div class="metric">Average Sentence Length: {report.avg_sentence_length} words</div>
            <div class="metric">Vocabulary Richness: {report.vocabulary_richness:.1%}</div>
            <div class="metric">Dialogue Percentage: {report.dialogue_percentage:.1%}</div>
            <div class="metric">Average Chapter Length: {report.avg_chapter_length:,.0f} words</div>
            <div class="metric">Average Scene Length: {report.avg_scene_length:,.0f} words</div>
        </div>
        
        <div class="section">
            <h3>Main Characters</h3>
            <table>
                <tr><th>Character</th><th>Mentions</th></tr>
    """
    
    for name, char in list(report.main_characters.items())[:10]:
        html_content += f"<tr><td>{name}</td><td>{char.count}</td></tr>\n"
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h3>Pacing Analysis</h3>
    """
    
    if report.pacing_analysis:
        for metric, value in report.pacing_analysis.items():
            html_content += f'<div class="metric">{metric.replace("_", " ").title()}: {value:.3f}</div>\n'
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    output_path.write_text(html_content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Analyze complete novel structure using spaCy NLP"
    )
    parser.add_argument("input", help="Path to the novel text file")
    parser.add_argument("--output", help="JSON output file path")
    parser.add_argument("--html", help="HTML report output path")
    parser.add_argument("--title", default="", help="Novel title")
    parser.add_argument("--model", default="en_core_web_md", help="spaCy model to use")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    
    # Read the novel
    print(f"Reading novel from {input_path}...")
    text = input_path.read_text(encoding='utf-8', errors='ignore')
    
    title = args.title or input_path.stem
    
    # Initialize analyzer and process
    analyzer = NovelAnalyzer(args.model)
    report = analyzer.analyze_novel(text, title)
    
    # Print summary
    print(f"\n=== Novel Analysis Summary ===")
    print(f"Title: {report.title}")
    print(f"Total words: {report.total_words:,}")
    print(f"Chapters: {report.chapter_count}")
    print(f"Scenes: {report.scene_count}")
    print(f"Reading time: {report.estimated_read_time_hours:.1f} hours")
    print(f"Average sentence length: {report.avg_sentence_length} words")
    print(f"Dialogue percentage: {report.dialogue_percentage:.1%}")
    
    if report.main_characters:
        print(f"\nMain characters:")
        for name, char in list(report.main_characters.items())[:5]:
            print(f"  {name}: {char.count} mentions")
    
    # Save outputs
    if args.output:
        output_path = Path(args.output)
        output_data = asdict(report)
        # Convert sets to lists for JSON serialization
        def convert_sets_to_lists(obj):
            if isinstance(obj, dict):
                return {k: convert_sets_to_lists(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets_to_lists(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            else:
                return obj
        
        output_data = convert_sets_to_lists(output_data)
        output_path.write_text(json.dumps(output_data, indent=2), encoding='utf-8')
        print(f"\nJSON report saved to: {output_path}")
    
    if args.html:
        html_path = Path(args.html)
        generate_html_report(report, html_path)
        print(f"HTML report saved to: {html_path}")


if __name__ == "__main__":
    main()
