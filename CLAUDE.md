# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FFA Lab 9 is an educational MCP (Model Context Protocol) implementation demonstrating secure, production-ready emotion arc analysis tools. The project showcases proper Python packaging, Docker deployment, security best practices, and educational examples for students.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (now using version ranges for compatibility)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Quick MCP setup (includes all dependencies)
./scripts/setup_mcp_development.sh
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov=examples

# Run specific test module
pytest tests/test_emotion_arc.py -v

# Run a single test
pytest tests/test_emotion_arc.py::test_sentence_scoring -v
```

### Code Quality
```bash
# Format code (now includes examples/)
black tools/ examples/

# Lint code
flake8 tools/ examples/

# Type checking
mypy tools/ --ignore-missing-imports

# Install and use pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Running Core Tools
```bash
# Basic emotion analysis
python tools/chapter_emotion_arc.py samples/sample_chapter.txt --window 5 --csv emotions.csv

# Start MCP server (secured with input validation)
python tools/emotion_arc_mcp_server.py --config config/mcp_server_config.yaml

# Start FastAPI server (with rate limiting)
python tools/emotion_arc_api_server.py --config config/api_server_config.yaml
# Access docs at: http://localhost:8000/docs

# Use simplified Docker deployment
docker-compose -f docker-compose.simple.yml up
```

### Running Educational Examples
```bash
# Extended analysis tools (moved to examples/)
python examples/writing_analysis/chapter_lexical_diversity.py samples/sample.txt
python examples/writing_analysis/writers_room_v2.py --input samples/sample.txt --output-dir output/

# Quick analysis script
python scripts/quick_analyze.py samples/sample.txt
```

## Current Architecture

### Core Tools (`tools/` - 5 files)
**Production MCP/API servers:**
- `chapter_emotion_arc.py` - Core emotion analysis logic
- `emotion_arc_mcp_server.py` - MCP server with security features
- `emotion_arc_api_server.py` - FastAPI REST server
- `emotion_arc_stdio_server.py` - Stdio communication variant
- `memory_mcp.py` - Memory management for AI assistants

### Educational Examples (`examples/writing_analysis/` - 11 files)
**Student learning tools:**
- `chapter_*.py` - 7 specialized analysis modules
- `writers_room_v2.py` - Multi-tool orchestration
- `emotion_report_generator.py` - Report generation
- `generate_html_comparison.py` - Visual comparisons
- `apply_editing_plan.py` - Automated editing

### Integration Points
- **MCP Protocol**: `emotion_arc_mcp_server.py` exposes tools to AI assistants like Claude
- **REST API**: `emotion_arc_api_server.py` provides HTTP endpoints
- **Docker**: Multi-stage builds for development and production
- **Security**: Input validation, rate limiting, path traversal protection

### Data Flow
1. Text input → Core analysis (`tools/chapter_emotion_arc.py`) → Structured output
2. MCP/API servers provide secure external access
3. Educational examples show extended analysis patterns

## Security Features (v1.1.0+)

### Input Validation
- Text sanitization (removes control characters, null bytes)
- Path validation (prevents directory traversal)
- Size limits (100KB max input)
- Pydantic models with strict typing

### Rate Limiting
- 60 requests/minute per IP (configurable)
- Per-endpoint limits available
- Automatic cleanup of tracking data

### Docker Security
- Non-root user execution (`appuser`)
- Security updates applied during build
- Minimal base images (python:3.11-slim)
- .dockerignore optimized for build context

## Key Implementation Patterns

### Error Handling
- Structured error responses with proper HTTP status codes
- Sanitized error messages (no internal details leaked)
- Comprehensive logging for debugging
- Try/except blocks with fallback behavior

### Output Formats
- JSON with metadata (timestamp, version, parameters)
- CSV with descriptive headers
- Markdown for human-readable reports
- Consistent structure across all tools

### Testing Approach
- Unit tests in `tests/` directory (9 test files)
- CI/CD pipeline testing Python 3.8-3.11
- Docker build testing
- Integration tests for MCP/API servers

## Configuration

### MCP Server (`config/mcp_server_config.yaml`)
- Server settings with security parameters
- Rate limiting configuration
- Logging and file size limits
- Security settings (input validation, path restrictions)

### API Server (`config/api_server_config.yaml`)
- FastAPI configuration with CORS settings
- Rate limiting per endpoint
- Security validation options
- Docker-friendly defaults

### Claude Desktop Integration (`config/claude_desktop_config.json`)
- MCP server registration for Claude Desktop
- Proper stdio server configuration
- Ready for copy to Claude config directory

## Important Notes

### Security Considerations
- All user input is sanitized before processing
- Version ranges prevent supply chain attacks
- Docker containers run as non-root users
- Rate limiting prevents DoS attacks
- Path validation prevents directory traversal

### File Organization
- `tools/` contains production-ready MCP/API code
- `examples/` contains educational and extended analysis tools
- `docs/` has comprehensive documentation including dependency management
- `config/` has secure default configurations
- Root directory is clean with only essential files

### Dependencies
- Requirements use version ranges for Python 3.8-3.11 compatibility
- All packages pinned to secure, compatible versions
- Optional dependencies separated for minimal installs
- Development dependencies isolated in requirements-dev.txt

### Docker Deployment
- `Dockerfile.mcp` - Secured container for MCP server
- `docker-compose.simple.yml` - Minimal deployment (recommended)
- `docker-compose.yml` - Full development environment
- Multi-stage builds optimize for production vs development

## Troubleshooting

### MCP Server Issues
- Check logs in `mcp-server-emotion-arc-analyzer.log`
- Ensure Claude Desktop config points to correct stdio server
- Verify import paths for moved modules (emotion_report_generator)

### CI/CD Failures
- Python 3.8 compatibility requires specific package versions
- Missing dependencies need to be added to requirements.txt
- Docker builds need .dockerignore optimization

### Import Errors
- Use PYTHONPATH when running from different directories
- Check `__init__.py` files for proper package structure
- Update import paths when files are moved between directories