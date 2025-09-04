# Building AI Tools for Authors: An Educational Guide

## Introduction to Model Context Protocol (MCP)

The Model Context Protocol (MCP) is a standardized way for AI assistants to access external tools and data sources. In this educational project, we're building MCP tools specifically designed to help authors and writers with their craft.

## What Makes a Good MCP Tool?

### 1. Single Responsibility
Each tool should do one thing well. For example:
- `chapter_emotion_arc.py` focuses only on emotional analysis
- `chapter_dialogue.py` focuses only on dialogue patterns
- `memory_mcp.py` focuses only on memory management

### 2. Clear Input/Output
- **Input**: Text files, configuration parameters
- **Output**: Structured data (JSON, CSV) with clear metrics
- **Interface**: Command-line arguments that are self-documenting

### 3. Educational Value
Since this is a learning project, each tool demonstrates:
- Text processing techniques
- Statistical analysis methods
- Data structure design
- Modular programming principles

## Architecture Overview

```
Author's Text Input
        ↓
[Text Processing Layer]
        ↓
[Analysis Engine]
        ↓ 
[Results Formatter]
        ↓
Structured Output (JSON/CSV)
```

## Core Concepts Demonstrated

### Text Processing Fundamentals

**Sentence Segmentation**
```python
def sentences(text: str) -> List[str]:
    """Split text into sentences using regex patterns."""
    # Simple but effective approach for educational purposes
```

**Tokenization**
```python  
def tokens(sentence: str) -> List[str]:
    """Extract words from a sentence."""
    # Demonstrates basic NLP preprocessing
```

### Lexicon-Based Analysis

Our tools use small, curated word lists rather than complex machine learning models. This approach is:
- **Transparent**: Students can see exactly how scoring works
- **Modifiable**: Easy to extend with domain-specific terms
- **Fast**: No external dependencies or model loading
- **Educational**: Teaches fundamental text analysis concepts

### Statistical Metrics

**Rolling Averages**
```python
def rolling(values: List[float], window: int) -> List[float]:
    """Compute rolling averages to smooth noisy data."""
    # Teaches smoothing techniques for time-series data
```

**Diversity Measures**
- Type-Token Ratio (vocabulary richness)
- Sentence length variation
- Readability scores

### Data Structures

**Structured Results**
```python
@dataclass
class SentenceScore:
    """Container for sentence-level analysis results."""
    index: int
    valence: float
    emotions: Dict[str, int]
    text: str
```

## Building Your Own MCP Tool

### Step 1: Define Your Analysis Goal

Ask yourself:
- What aspect of writing am I analyzing?
- What would be useful feedback for an author?
- How can I measure this objectively?

### Step 2: Design Your Data Structures

Create clear classes or dictionaries to hold:
- Input parameters
- Intermediate calculations  
- Final results

### Step 3: Implement Core Logic

Follow the pattern:
1. **Parse input** (text file, command-line args)
2. **Process text** (sentence splitting, tokenization)
3. **Apply analysis** (scoring, counting, measuring)
4. **Generate results** (statistics, summaries, visualizations)

### Step 4: Add Educational Elements

- Clear variable names
- Explanatory comments
- Usage examples in docstrings
- Simple, readable algorithms

### Step 5: Test and Document

- Create test cases with known inputs/outputs
- Write clear usage instructions
- Provide example files

## Common Patterns

### Command Line Interface
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("input_file", help="Path to text file")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()
    
    # Process and analyze
    # Generate output
```

### File Processing
```python
def analyze_file(file_path: str) -> AnalysisResult:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split into sentences
    # Analyze each sentence  
    # Aggregate results
    
    return results
```

### Output Generation
```python
def save_results(results: AnalysisResult, output_path: str):
    if output_path.endswith('.json'):
        with open(output_path, 'w') as f:
            json.dump(asdict(results), f, indent=2)
    elif output_path.endswith('.csv'):
        # CSV output logic
```

## Integration with AI Assistants

Once you have working analysis tools, they can be integrated with AI assistants in several ways:

### Direct File Processing
```bash
python chapter_emotion_arc.py manuscript.txt --json emotions.json
# AI assistant can read emotions.json to provide feedback
```

### Memory Integration  
```python
from memory_mcp import MemoryTool

memory = MemoryTool()
memory.add_memory(
    topic="chapter_1_analysis",
    summary="High tension in opening, needs more joy",
    tags=["emotion", "pacing", "chapter1"]
)
```

### Workflow Orchestration
```python
# writers_room_v2.py coordinates multiple tools
results = {
    'emotions': analyze_emotions(text),
    'dialogue': analyze_dialogue(text), 
    'structure': analyze_structure(text)
}
```

## Advanced Topics

### Custom Lexicons
Extend the built-in word lists for your genre:
```python
GENRE_SPECIFIC_WORDS = {
    'mystery': {'clue', 'suspect', 'alibi', 'murder'},
    'romance': {'love', 'heart', 'kiss', 'passion'},
    'sci-fi': {'space', 'alien', 'technology', 'future'}
}
```

### Visualization
Add matplotlib charts to your tools:
```python
import matplotlib.pyplot as plt

def plot_emotion_arc(scores: List[float]):
    plt.plot(scores)
    plt.title("Emotional Arc") 
    plt.xlabel("Sentence Number")
    plt.ylabel("Valence Score")
    plt.savefig("emotion_arc.png")
```

### Web Interfaces
Convert command-line tools to web services:
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze/emotions")
async def analyze_emotions_endpoint(text: str):
    results = analyze_emotions(text)
    return results
```

## Learning Exercises

1. **Extend an existing tool** - Add new emotion categories to `chapter_emotion_arc.py`

2. **Create a new analysis** - Build a tool to measure dialogue balance between characters

3. **Add visualization** - Create charts for any of the existing analysis tools

4. **Build a web interface** - Convert a command-line tool to a web API

5. **Improve integration** - Enhance the memory system with search and filtering

## Conclusion

This project demonstrates how to build practical, educational AI tools for authors. The key principles are:

- **Simplicity**: Use basic techniques that students can understand and modify
- **Modularity**: Build small, focused tools that can be combined
- **Transparency**: Make the analysis process visible and explainable  
- **Extensibility**: Design tools that can be easily enhanced and customized

By following these patterns, students learn both practical programming skills and the fundamentals of building AI-assisted creative tools.
