# Sample Files Organization

This directory contains organized sample files for testing and demonstrating the writing analysis tools.

## Directory Structure

### 📁 `test_cases/`
**Purpose**: Curated sample files designed to test specific tool functionality
- Files created specifically to demonstrate tool capabilities
- Known emotional patterns and structures
- Used for educational examples and documentation

**Current files**:
- `emotional_journey.txt` - Complex emotional arc with multiple transitions
- `sample_chapter.txt` - Basic story progression for initial testing

### 📁 `user_content/`
**Purpose**: Your original writing and real-world content for analysis
- Place your own chapters, stories, and manuscripts here
- Real-world testing of the tools
- Personal writing analysis and improvement

**Recommended naming convention**:
- `chapter_01_opening.txt`
- `chapter_05_climax.txt` 
- `my_story_draft_v1.txt`
- `dialogue_scene_cafe.txt`

### 📁 `../output/`
**Purpose**: Generated analysis results and reports
- CSV files with detailed sentence-by-sentence data
- JSON files with summary statistics and trends
- HTML comparison reports (when available)
- Charts and visualizations (future feature)

## Usage Recommendations

### For Your Own Content
```bash
# Place your chapter in user_content/
cp /path/to/your/chapter.txt samples/user_content/my_chapter.txt

# Analyze with output saved to output directory
python tools/chapter_emotion_arc.py samples/user_content/my_chapter.txt \
  --csv output/my_chapter_emotions.csv \
  --json output/my_chapter_emotions.json
```

### For Testing and Learning
```bash
# Use test cases for learning how the tool works
python tools/chapter_emotion_arc.py samples/test_cases/emotional_journey.txt

# Compare different window sizes
python tools/chapter_emotion_arc.py samples/test_cases/emotional_journey.txt --window 2
python tools/chapter_emotion_arc.py samples/test_cases/emotional_journey.txt --window 5
```

## File Naming Best Practices

### For User Content
- Use descriptive names: `chapter_03_confrontation.txt`
- Include version numbers: `story_draft_v2.txt`
- Indicate content type: `dialogue_heavy_scene.txt`
- Use consistent naming: `book1_ch01.txt`, `book1_ch02.txt`

### For Generated Output
- Match input filename: `my_chapter_emotions.csv`
- Include analysis type: `chapter_03_emotions.json`
- Add timestamps for versions: `story_analysis_2025-09-04.csv`

## File Size Considerations

- **Small files** (< 1KB): Quick testing, specific scenes
- **Medium files** (1-10KB): Typical chapter length, good for most analysis
- **Large files** (> 10KB): Full stories, performance testing

The emotion arc tool handles files up to novel length efficiently.

## Privacy and Sharing

### User Content Directory
- Add `samples/user_content/` to `.gitignore` if content is private
- Use generic filenames if sharing analysis results
- Consider copyright when using published text

### Test Cases Directory  
- Safe to share and commit to version control
- Designed for educational and demonstration purposes
- Feel free to add your own test cases for the community

## Getting Started

1. **Place your chapter** in `samples/user_content/`
2. **Run the analysis**:
   ```bash
   python tools/chapter_emotion_arc.py samples/user_content/your_chapter.txt \
     --csv output/analysis.csv --json output/analysis.json
   ```
3. **Review results** in the `output/` directory
4. **Experiment** with different window sizes and compare results

Happy analyzing! 📝✨
