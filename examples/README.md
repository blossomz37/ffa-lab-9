# Examples Directory

This directory contains example projects and educational tools for students learning about text analysis and MCP development.

## Structure

### `/writing_analysis/`
Extended writing analysis tools that demonstrate various NLP techniques:

**Core Analysis Tools:**
- `chapter_beats_detection.py` - Detect narrative beats and pacing
- `chapter_character_dialogue.py` - Analyze dialogue patterns and character voice
- `chapter_continuity_consistency.py` - Check for plot/character consistency
- `chapter_lexical_diversity.py` - Measure vocabulary richness
- `chapter_mechanics_cleanup.py` - Identify mechanical writing issues
- `chapter_structural_analysis.py` - Analyze story structure
- `chapter_style_readability.py` - Assess readability and style

**Utility Tools:**
- `writers_room_v2.py` - Orchestrates multiple analysis tools
- `emotion_report_generator.py` - Generate comprehensive emotion reports
- `generate_html_comparison.py` - Create visual HTML comparisons
- `apply_editing_plan.py` - Apply automated editing suggestions

## For Students

These examples demonstrate:
1. **Text Processing** - Tokenization, sentence splitting, pattern matching
2. **Lexicon-Based Analysis** - Using word lists for sentiment/emotion
3. **Statistical Analysis** - Computing metrics like diversity, readability
4. **Pattern Detection** - Finding dialogue, narrative beats, consistency issues
5. **Report Generation** - Creating structured output in various formats

### Getting Started

1. Each script can be run standalone:
   ```bash
   python examples/writing_analysis/chapter_lexical_diversity.py sample.txt
   ```

2. Use `writers_room_v2.py` to run multiple analyses:
   ```bash
   python examples/writing_analysis/writers_room_v2.py --input sample.txt --output-dir results/
   ```

3. Study the code to understand different analysis techniques

### Project Ideas

- Extend lexicons for genre-specific analysis
- Add new emotion categories
- Create visualizations of the metrics
- Build a web interface for the tools
- Integrate with machine learning models
- Add support for other languages

## Note

These are educational examples. For production use, consider:
- More comprehensive lexicons
- Machine learning models
- Performance optimization
- Error handling improvements
- Security hardening