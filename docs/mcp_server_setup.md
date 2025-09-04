# MCP Server Setup Guide

## Overview

This guide walks you through setting up the Model Context Protocol (MCP) server for emotion arc analysis. The MCP server allows AI assistants like Claude to analyze text for emotional progression using our `chapter_emotion_arc.py` tool.

## Prerequisites

### System Requirements
- **macOS**: macOS 10.14 or later
- **Python**: Version 3.8 or higher
- **Memory**: At least 1GB RAM available
- **Disk Space**: ~200MB for dependencies

### Check Your Setup
```bash
# Verify Python version
python3 --version

# Check if you're in the right directory
ls -la | grep requirements.txt

# Verify you have the project files
ls tools/chapter_emotion_arc.py
```

## Quick Setup (Automated)

The fastest way to get started:

```bash
# 1. Make the setup script executable
chmod +x scripts/setup_mcp_development.sh

# 2. Run the automated setup
./scripts/setup_mcp_development.sh

# 3. Activate the environment
source venv/bin/activate

# 4. Test the basic functionality
python scripts/test_mcp_server.py
```

## Manual Setup (Step-by-Step)

If you prefer to understand each step or the automated setup fails:

### Step 1: Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip to latest version
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Verify MCP installation
python -c "import mcp; print('✅ MCP installed successfully')"
```

### Step 2: Test Basic Functionality

```bash
# Test the original tool
python tools/chapter_emotion_arc.py samples/sample_chapter.txt --json /tmp/test.json

# Verify output
cat /tmp/test.json
```

### Step 3: Test MCP Server Components

```bash
# Run the test suite
python scripts/test_mcp_server.py

# Run interactive testing
python scripts/test_mcp_server.py --interactive
```

## Understanding the MCP Implementation

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Protocol   │◄──►│  Emotion Arc    │
│   (Claude, etc) │    │     (Server)     │    │    Analyzer     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                       ┌──────────────────┐
                       │  Original Tool   │
                       │ chapter_emotion_ │
                       │     arc.py       │
                       └──────────────────┘
```

### Key Components

1. **MCP Server** (`tools/emotion_arc_mcp_server.py`)
   - Implements the MCP protocol
   - Handles tool requests from AI assistants
   - Manages input validation and error handling

2. **Emotion Arc Analyzer** (wrapper class)
   - Encapsulates the original analysis logic
   - Provides async interface
   - Handles multiple output formats

3. **Original Tool** (`tools/chapter_emotion_arc.py`)
   - Core analysis functionality
   - Lexicon-based sentiment analysis
   - Rolling window calculations

## Usage Examples

### Basic Analysis

```bash
# Start the MCP server (in one terminal)
python tools/emotion_arc_mcp_server.py

# Test with a simple text
python scripts/test_mcp_server.py --text "I am happy today but worried about tomorrow."
```

### Different Output Formats

```bash
# JSON output (default)
python scripts/test_mcp_server.py --text "Sample text" --format json

# CSV output
python scripts/test_mcp_server.py --text "Sample text" --format csv

# Markdown report
python scripts/test_mcp_server.py --text "Sample text" --format markdown
```

### Interactive Testing

```bash
python scripts/test_mcp_server.py --interactive
```

## Integration with AI Assistants

### Claude Desktop Integration

1. **Install Claude Desktop** (if not already installed)
2. **Configure MCP Tool** in Claude's settings:
   ```json
   {
     "mcpServers": {
       "emotion-arc-analyzer": {
         "command": "python",
         "args": ["/path/to/ffa-lab-9/tools/emotion_arc_mcp_server.py"],
         "env": {
           "PYTHONPATH": "/path/to/ffa-lab-9"
         }
       }
     }
   }
   ```

3. **Test Integration**:
   - Open Claude Desktop
   - Try: "Analyze the emotional arc of this text: [your text here]"

### Other AI Assistants

The MCP server follows the standard MCP protocol, so it should work with any MCP-compatible AI assistant. Check your AI assistant's documentation for specific setup instructions.

## Configuration

### Server Configuration

Edit `config/mcp_server_config.yaml`:

```yaml
server:
  host: "localhost"
  port: 8000
  debug: true

analysis:
  default_window_size: 5
  max_text_length: 100000
  supported_formats: ["json", "csv", "markdown"]

logging:
  level: "INFO"
  file: "logs/mcp_server.log"
```

### Custom Lexicons

You can extend the emotion lexicons by modifying the `POS`, `NEG`, and `EMO` dictionaries in `chapter_emotion_arc.py`.

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'mcp'
# Solution:
pip install mcp pydantic

# Error: Import "emotion_arc_mcp_server" could not be resolved
# Solution: Make sure you're running from the project root directory
cd /path/to/ffa-lab-9
python scripts/test_mcp_server.py
```

#### 2. Virtual Environment Issues
```bash
# Error: Command not found or wrong Python version
# Solution: Make sure virtual environment is activated
source venv/bin/activate
which python  # Should show path in venv/bin/python
```

#### 3. Permission Errors
```bash
# Error: Permission denied
# Solution: Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

#### 4. Port Already in Use
```bash
# Error: Address already in use
# Solution: Kill existing processes or use different port
lsof -ti:8000 | xargs kill -9
# Or edit config to use different port
```

### Debug Mode

Enable detailed logging:

```bash
# Set debug mode
export DEBUG=1

# Run with verbose output
python tools/emotion_arc_mcp_server.py --config config/dev.yaml
```

### Log Files

Check log files for detailed error information:

```bash
# View recent logs
tail -f logs/mcp_server.log

# Search for errors
grep ERROR logs/mcp_server.log
```

## Performance Considerations

### Text Length Limits

- **Default maximum**: 100,000 characters
- **Recommended**: Under 50,000 characters for best performance
- **Minimum**: At least 10 characters for meaningful analysis

### Memory Usage

- **Typical usage**: 50-100MB per analysis
- **Large texts**: Up to 500MB for very long documents
- **Concurrent requests**: ~100MB per simultaneous analysis

### Response Times

- **Short texts** (< 1,000 chars): < 1 second
- **Medium texts** (1,000-10,000 chars): 1-3 seconds
- **Long texts** (10,000+ chars): 3-10 seconds

## Advanced Topics

### Custom Tools

To create additional MCP tools based on other analysis scripts:

1. Create a new server file following the `emotion_arc_mcp_server.py` template
2. Import your analysis tool
3. Define the tool schema in `handle_list_tools()`
4. Implement the analysis logic in `handle_call_tool()`

### Multiple Tool Server

You can extend the server to support multiple analysis tools:

```python
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        emotion_arc_tool(),
        dialogue_analysis_tool(),
        style_analysis_tool(),
        # Add more tools here
    ]
```

### Batch Processing

For analyzing multiple texts:

```python
# Example: Analyze multiple chapters
texts = ["Chapter 1 text...", "Chapter 2 text...", "Chapter 3 text..."]
results = []

for i, text in enumerate(texts):
    result = await analyzer.analyze_text(EmotionArcRequest(text=text))
    results.append({"chapter": i+1, "analysis": result})
```

## Educational Exercises

### Exercise 1: Extend the Lexicon
Add genre-specific emotion words:

1. Edit `chapter_emotion_arc.py`
2. Add new words to the `EMO` dictionary
3. Test with genre-specific texts
4. Compare results before and after

### Exercise 2: Add Visualization
Create a plotting tool:

1. Install matplotlib: `pip install matplotlib`
2. Add a new output format: "plot"
3. Generate emotion arc charts
4. Save as PNG files

### Exercise 3: Build a Web Interface
Create a simple web UI:

1. Use FastAPI to create web endpoints
2. Add HTML forms for text input
3. Display results in the browser
4. Add file upload capability

### Exercise 4: Multi-Language Support
Extend for other languages:

1. Create Spanish/French emotion lexicons
2. Add language detection
3. Use appropriate lexicon based on detected language
4. Test with multilingual texts

## Next Steps

1. **Complete the MCP Integration**: Follow the refined task list
2. **Test with Real AI Assistants**: Try Claude Desktop integration
3. **Extend to Other Tools**: Convert other analysis scripts to MCP
4. **Share with Students**: Use this as a teaching example
5. **Contribute Back**: Add improvements to the project

## Getting Help

- **Check the logs**: `logs/mcp_server.log`
- **Run diagnostics**: `python scripts/test_mcp_server.py`
- **Review documentation**: `docs/ai-tools-guide.md`
- **Ask questions**: Create GitHub issues for problems

---

**Happy analyzing! 📊✨**
