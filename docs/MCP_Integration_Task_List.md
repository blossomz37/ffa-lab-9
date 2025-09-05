# MCP Integration Task List - Refined for Educational Success

## Overview
Transform `chapter_emotion_arc.py` into a proper Model Context Protocol (MCP) server that can be used by AI assistants like Claude, GPT, etc. This implementation prioritizes educational value and cross-platform compatibility (especially macOS).

## Phase 1: Foundation Setup (Essential)

### 1. Environment Preparation (Mac-Optimized)
- [ ] **Verify Python Environment**
  - [ ] Ensure Python 3.8+ is installed (`python3 --version`)
  - [ ] Create isolated virtual environment (`python3 -m venv venv`)
  - [ ] Activate environment (`source venv/bin/activate` on macOS/Linux)
  - [ ] Install core dependencies (`pip install -r requirements.txt`)
  
- [ ] **Install MCP Dependencies**
  - [ ] Add `mcp` package to requirements.txt (`pip install mcp>=0.1.0`)
  - [ ] Add `pydantic>=2.0.0` for data validation
  - [ ] Add `asyncio` support libraries if needed
  - [ ] Test installation with `python -c "import mcp; print('MCP installed successfully')"`

### 2. MCP Server Architecture Design
- [ ] **Define MCP Tool Specification**
  - [ ] Create `tools/emotion_arc_mcp_server.py` as main server file
  - [ ] Define tool schema following MCP protocol:
    ```json
    {
      "name": "emotion_arc_analyzer",
      "description": "Analyzes emotional progression in text using sentiment lexicons",
      "inputSchema": {
        "type": "object",
        "properties": {
          "text": {"type": "string", "description": "Text to analyze"},
          "window_size": {"type": "integer", "default": 5},
          "output_format": {"type": "string", "enum": ["json", "csv", "markdown"]}
        },
        "required": ["text"]
      }
    }
    ```

- [ ] **Refactor Core Functionality**
  - [ ] Extract analysis logic from `chapter_emotion_arc.py` into reusable functions
  - [ ] Create `EmotionArcAnalyzer` class with methods:
    - [ ] `analyze_text(text: str, window: int = 5) -> AnalysisResult`
    - [ ] `format_output(result: AnalysisResult, format: str) -> str`
    - [ ] `validate_input(text: str, window: int) -> bool`

### 3. MCP Server Implementation
- [ ] **Create Base MCP Server**
  - [ ] Implement MCP protocol handlers (initialize, list_tools, call_tool)
  - [ ] Add proper async/await patterns for MCP compliance
  - [ ] Include error handling with MCP-compliant error responses
  - [ ] Add logging with configurable levels (DEBUG, INFO, WARNING, ERROR)

- [ ] **Tool Integration**
  - [ ] Wire `EmotionArcAnalyzer` into MCP tool handler
  - [ ] Implement input validation and sanitization
  - [ ] Add output formatting for all supported formats (JSON, CSV, Markdown)
  - [ ] Include metadata in responses (analysis timestamp, parameters used, etc.)

## Phase 2: Local Development & Testing

### 4. Development Environment
- [ ] **Local Testing Setup**
  - [ ] Create `scripts/test_mcp_server.py` for local testing
  - [ ] Add sample test texts in `samples/mcp_test_cases/`
  - [ ] Create `scripts/start_dev_server.py` with hot-reload
  - [ ] Add environment variables file (`.env.example`)

- [ ] **Testing Framework**
  - [ ] Write unit tests for `EmotionArcAnalyzer` class
  - [ ] Write integration tests for MCP server endpoints
  - [ ] Add performance tests for different text sizes
  - [ ] Create test cases for edge conditions (empty text, very long text)
  - [ ] Ensure all tests pass on macOS with `pytest tests/test_mcp_*`

### 5. Documentation & Examples
- [ ] **User Documentation**
  - [ ] Create `docs/mcp_server_setup.md` with step-by-step installation
  - [ ] Add macOS-specific instructions and troubleshooting
  - [ ] Include example usage with popular AI assistants
  - [ ] Document all MCP tool parameters and expected outputs

- [ ] **Developer Documentation**
  - [ ] Add docstrings to all classes and methods
  - [ ] Create API reference documentation
  - [ ] Include architecture diagrams showing MCP flow
  - [ ] Add contribution guidelines for extending the server

## Phase 3: Production Readiness

### 6. Configuration & Deployment
- [ ] **Configuration Management**
  - [ ] Create `config/mcp_server_config.yaml` for settings
  - [ ] Add environment-based configuration (dev, test, prod)
  - [ ] Include configurable lexicons and analysis parameters
  - [ ] Add rate limiting and security configurations

- [ ] **Local Deployment Options**
  - [ ] Create startup scripts for macOS (`scripts/start_mcp_server.sh`)
  - [ ] Add systemd service file for Linux users
  - [ ] Create Docker Compose setup for containerized deployment
  - [ ] Include reverse proxy configuration (nginx) if needed

### 7. Advanced Features (Optional)
- [ ] **Multi-Tool Server**
  - [ ] Extend server to include other analysis tools
  - [ ] Add tool discovery and dynamic loading
  - [ ] Implement tool chaining for complex workflows
  - [ ] Add memory/state management between tool calls

- [ ] **Performance Optimization**
  - [ ] Add async processing for large texts (only if needed)
  - [ ] Implement caching for repeated analyses
  - [ ] Add streaming responses for real-time analysis
  - [ ] Include progress reporting for long-running tasks

## Phase 4: Educational Materials

### 8. Student Resources
- [ ] **Tutorial Creation**
  - [ ] Write step-by-step tutorial: "Building Your First MCP Server"
  - [ ] Create video walkthrough for setup process
  - [ ] Add troubleshooting guide for common issues
  - [ ] Include exercises for extending the server

- [ ] **Example Integrations**
  - [ ] Show integration with Claude Desktop
  - [ ] Demonstrate usage with Cline VS Code extension
  - [ ] Add examples for other MCP-compatible tools
  - [ ] Create sample automation workflows

## Quick Start Commands (macOS)

```bash
# 1. Environment setup
cd ffa-lab-9
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install MCP dependencies
pip install mcp pydantic

# 3. Test core functionality
python tools/chapter_emotion_arc.py samples/sample_chapter.txt --json test.json

# 4. Start MCP server (once implemented)
python tools/emotion_arc_mcp_server.py --config config/dev.yaml

# 5. Test MCP integration
python scripts/test_mcp_server.py
```

## Success Criteria
- [ ] MCP server starts successfully on macOS without errors
- [ ] Can analyze text and return results in all supported formats
- [ ] Integrates with at least one AI assistant (Claude Desktop recommended)
- [ ] Passes all tests on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- [ ] Documentation is complete and beginner-friendly
- [ ] Students can follow tutorial to create their own MCP tools

## Fallback Options
If full MCP implementation proves too complex:
- [ ] **HTTP API Server**: Create FastAPI server with similar functionality
- [ ] **Command Line Tool Enhancement**: Add JSON output and scripting support
- [ ] **VS Code Extension**: Build extension using existing tools

---

**Next Steps**: Start with Phase 1, focusing on environment setup and basic MCP server structure. Test frequently on macOS to ensure compatibility.
