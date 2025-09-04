# Chapter Emotion Arc Analysis Tool

A comprehensive tool for analyzing the emotional journey within text using lexicon-based sentiment analysis and rolling averages.

## Overview

The `chapter_emotion_arc.py` tool analyzes text to detect emotional patterns and progression through a chapter or story. It uses small, curated word lists (lexicons) to identify emotions and compute both sentence-level and smoothed trend data.

## Key Features

- **Sentiment Analysis**: Detects positive and negative emotional valence
- **Multi-Emotion Detection**: Tracks 8 specific emotions (joy, sadness, anger, fear, trust, disgust, surprise, anticipation)
- **Rolling Averages**: Smooths emotional data to show trends and arcs
- **Multiple Output Formats**: Console summary, CSV data, and JSON results
- **Robust Error Handling**: Gracefully handles edge cases and file errors
- **Performance Optimized**: Handles large texts efficiently

## Installation & Usage

### Basic Usage

```bash
python chapter_emotion_arc.py input.txt
```

### Advanced Usage

```bash
python chapter_emotion_arc.py input.txt --window 3 --csv emotions.csv --json emotions.json
```

### Command Line Options

- `input`: Path to the text file to analyze (required)
- `--window N`: Rolling window size in sentences (default: 5)
- `--csv FILE`: Output detailed CSV file with per-sentence data
- `--json FILE`: Output JSON file with summary and time series data

## Understanding the Output

### Console Output

```
=== Emotion Arc ===
File: samples/emotional_journey.txt
Sentences: 18 | Avg valence: 0.28 | Top emotions: ['fear', 'trust', 'joy']
(Rolling window = 3)
```

- **Sentences**: Total number of sentences analyzed
- **Avg valence**: Overall emotional tone (-1 negative to +1 positive)
- **Top emotions**: Most frequently detected emotions, ranked by occurrence
- **Rolling window**: Size of smoothing window applied

### CSV Output

The CSV file contains detailed sentence-by-sentence analysis:

- `sent_index`: Sentence number (0-based)
- `valence_raw`: Raw emotional valence for this sentence
- `valence_rolling`: Smoothed valence using rolling average
- `[emotion]_rolling`: Smoothed count for each emotion category

### JSON Output

The JSON file contains:
- `summary`: Overall statistics and top emotions
- `valence_rolling`: Array of smoothed valence scores
- `emotions_rolling`: Object with arrays for each emotion's progression

## Emotion Categories

The tool tracks these emotional dimensions:

1. **Joy**: happiness, delight, pleasure, amusement
2. **Sadness**: sorrow, grief, melancholy, despair  
3. **Anger**: rage, fury, irritation, annoyance
4. **Fear**: anxiety, terror, dread, worry
5. **Trust**: confidence, faith, security, safety
6. **Disgust**: revulsion, nausea, contempt
7. **Surprise**: shock, astonishment, amazement
8. **Anticipation**: expectation, hope, eagerness

## How It Works

### Text Processing

1. **Sentence Segmentation**: Splits text at sentence boundaries (. ! ?)
2. **Tokenization**: Extracts individual words, handling contractions and hyphens
3. **Normalization**: Converts to lowercase for lexicon matching

### Emotion Scoring

1. **Lexicon Matching**: Compares words against curated emotion word lists
2. **Valence Calculation**: Counts positive words minus negative words
3. **Emotion Counting**: Tallies occurrences of words in each emotion category

### Rolling Averages

1. **Smoothing**: Applies rolling window to reduce noise in emotional data
2. **Trend Detection**: Makes emotional arcs and patterns more visible
3. **Configurable Window**: Adjustable window size for different text lengths

## Example Analyses

### Detecting Emotional Arcs

For a story that starts with fear, transitions to hope, and ends with joy:

```
Sentence 1-3: High fear, low valence
Sentence 4-6: Decreasing fear, increasing trust  
Sentence 7-9: High joy, positive valence
```

### Understanding Rolling Averages

With window size 3:
- Raw scores: [0, -2, -1, 1, 2, 1]
- Rolling avg: [0, -1, -1, -0.67, 0.67, 1.33]

The rolling average smooths out spikes and shows clearer trends.

## Educational Applications

### Learning Text Analysis
- Demonstrates lexicon-based sentiment analysis
- Shows statistical smoothing techniques
- Teaches data structure design

### Creative Writing Analysis
- Identify pacing issues in emotional progression
- Ensure emotional variety across chapters
- Track character emotional development

### Computational Literature
- Quantify emotional patterns in different genres
- Compare authors' emotional styles
- Study emotional arcs in successful narratives

## Technical Details

### Lexicon Design

The tool uses small, curated word lists optimized for:
- **Transparency**: Easy to understand and modify
- **Speed**: Fast lookups without external dependencies
- **Accuracy**: Focused on high-confidence emotional words

### Performance Characteristics

- **Memory**: Linear with text length
- **Speed**: Processes ~1000 sentences per second
- **Scalability**: Handles texts up to novel length efficiently

### Error Handling

The tool gracefully handles:
- Non-existent files
- Empty or malformed text
- Unicode characters
- Invalid parameters
- File permission issues

## Extending the Tool

### Adding New Emotions

1. Define new emotion category in `EMO` dictionary
2. Add representative words for that emotion
3. Update output formatting to include new category

### Improving Lexicons

1. Add genre-specific emotional words
2. Include domain-specific terminology
3. Consider cultural and linguistic variations

### Advanced Features

Potential enhancements:
- Confidence scores for emotion detection
- Statistical significance testing
- Visualization output (charts/graphs)
- Multiple language support

## Troubleshooting

### Common Issues

**"File not found" error**
- Check file path is correct
- Ensure file exists and is readable

**Low emotion detection**
- Text may use different emotional vocabulary
- Consider extending lexicons with domain-specific words
- Try different window sizes

**Unexpected results**
- Check for abbreviations affecting sentence splitting
- Verify text encoding (should be UTF-8)
- Consider context-dependent emotional words

### Getting Help

1. Run with `--help` for usage information
2. Check error messages for specific issues
3. Test with sample files to verify installation
4. Review lexicons to understand detection scope

## Sample Files

The tool includes sample text files for testing:

- `samples/sample_chapter.txt`: Basic emotional progression
- `samples/emotional_journey.txt`: Complex emotional arc with multiple transitions

## Integration

The tool can be integrated into larger workflows:

```python
from chapter_emotion_arc import analyze

text = "Your story text here..."
scores, valence_rolling, emotions_rolling, summary = analyze(text, window=5)

print(f"Average valence: {summary.avg_valence}")
print(f"Top emotions: {summary.top_emotions}")
```

## License

This tool is released under the MIT License as part of the FFA Lab 9 educational project.
