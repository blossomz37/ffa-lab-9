# Novel Structural Analysis with spaCy

This directory contains two approaches to analyzing written works:

## Quickstart - Command Lines
To use the analysis tools:

1. Activate the environment:
   source nlp_env/bin/activate

2. Run the fast analysis:
   python3 chapter_structural_analysis.py your_chapter.txt

3. Run the comprehensive NLP analysis:
   python3 novel_structural_analysis.py your_novel.txt --output analysis.json --html report.html

4. Deactivate whe

## Scripts

### 1. `chapter_structural_analysis.py` (Original - Fast & Lightweight)
- **Purpose**: Quick structural analysis of individual chapters
- **Dependencies**: None (pure Python standard library)
- **Speed**: Very fast (milliseconds)
- **Analysis**: Basic structure, pacing, hook detection

**Usage:**
```bash
python3 chapter_structural_analysis.py path/to/chapter.txt --wpm 250 --json output.json
```

### 2. `novel_structural_analysis.py` (New - Advanced NLP)
- **Purpose**: Comprehensive analysis of complete novels
- **Dependencies**: spaCy, matplotlib (optional)
- **Speed**: Slower but more thorough (30 seconds to several minutes)
- **Analysis**: Characters, dialogue, sentiment, advanced structure

**Usage:**
```bash
# First-time setup
./setup_nlp_analysis.sh

# Analyze a novel
python3 novel_structural_analysis.py path/to/novel.txt --output analysis.json --html report.html
```

## What the NLP Version Adds

### Advanced Features:
- **Character Analysis**: Automatic character detection and tracking
- **Dialogue Detection**: Identifies and measures dialogue vs. narrative
- **Sentiment Analysis**: Tracks emotional arcs and tension
- **Scene Intelligence**: Smart scene detection beyond dividers
- **Chapter Structure**: Automatic chapter and act detection
- **Genre Analysis**: Writing style and pacing metrics

### Output Formats:
- **JSON**: Machine-readable detailed analysis
- **HTML**: Human-readable formatted report
- **Console**: Quick summary statistics

## Example Analysis Output

For a typical novel, the NLP version provides:

```
=== Novel Analysis Summary ===
Title: The Mystery Manuscript
Total words: 2,847
Chapters: 3
Scenes: 3
Reading time: 0.2 hours
Average sentence length: 18.5 words
Dialogue percentage: 15.2%

Main characters:
  Sarah: 12 mentions
  Dr. Morgan: 8 mentions
  Elizabeth: 3 mentions
```

## Installation

### Quick Setup (Recommended):
```bash
cd examples/writing_analysis/structural_analysis
./setup_nlp_analysis.sh
```

### Manual Setup:
```bash
# Install spaCy
pip install spacy matplotlib

# Download English language model
python -m spacy download en_core_web_md
```

## Test the Scripts

Try both scripts on the sample novel:

```bash
# Fast analysis (original script)
python3 chapter_structural_analysis.py sample_novel.txt

# Comprehensive analysis (NLP script)  
python3 novel_structural_analysis.py sample_novel.txt --html sample_report.html
```

## When to Use Which Script

### Use `chapter_structural_analysis.py` when:
- You need quick feedback while writing
- Working with individual chapters
- Want minimal dependencies
- Need real-time analysis

### Use `novel_structural_analysis.py` when:
- Analyzing complete manuscripts
- Need character and dialogue analysis
- Want detailed editorial reports
- Performing comprehensive manuscript evaluation

## Performance Comparison

| Feature | Original Script | NLP Script |
|---------|----------------|------------|
| **Speed** | ~5ms | ~30s-5min |
| **Dependencies** | None | spaCy + model |
| **Character Analysis** | None | Advanced |
| **Dialogue Detection** | None | Yes |
| **Sentiment Analysis** | Basic | Advanced |
| **Memory Usage** | Minimal | 100MB+ |
| **Best For** | Real-time feedback | Manuscript evaluation |

Both scripts are designed to complement each other for different stages of the writing and editing process.
