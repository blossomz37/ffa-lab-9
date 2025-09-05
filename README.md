# FFA Lab 9: MCP Emotion Arc Analysis Tools

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI/CD Pipeline](https://github.com/yourusername/ffa-lab-9/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ffa-lab-9/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Educational implementation of Model Context Protocol (MCP) servers for emotion and text analysis. This project demonstrates how to build secure, production-ready MCP tools that AI assistants like Claude can use for analyzing emotional progression in creative writing.

## 🎯 Project Overview

This repository provides:
- **MCP Server Implementation** - Complete emotion arc analysis exposed via MCP protocol
- **FastAPI REST Alternative** - HTTP API server for environments without MCP support
- **Security Best Practices** - Input validation, rate limiting, path traversal protection
- **Educational Examples** - Extended analysis tools for student projects

## 🚀 Quick Start

### Prerequisites
- Python 3.8-3.11
- pip package manager
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ffa-lab-9.git
cd ffa-lab-9

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (pinned versions for security)
pip install -r requirements.txt
```

### Basic Usage

#### 1. Run MCP Server
```bash
python tools/emotion_arc_mcp_server.py --config config/mcp_server_config.yaml
```

#### 2. Run FastAPI Server
```bash
python tools/emotion_arc_api_server.py --config config/api_server_config.yaml
# Visit http://localhost:8000/docs for interactive API documentation
```

#### 3. Analyze Text Directly
```bash
python tools/chapter_emotion_arc.py samples/sample_chapter.txt --window 5 --csv output.csv
```

#### 4. Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.mcp.yml up

# Or build manually
docker build -f Dockerfile.mcp -t emotion-mcp:latest .
docker run -p 8000:8000 emotion-mcp:latest
```

## 📁 Project Structure

```
ffa-lab-9/
├── tools/                     # Core MCP/API implementations
│   ├── emotion_arc_mcp_server.py      # MCP server with security features
│   ├── emotion_arc_api_server.py      # FastAPI REST server
│   ├── emotion_arc_stdio_server.py    # Stdio communication variant
│   ├── chapter_emotion_arc.py         # Core emotion analysis logic
│   └── memory_mcp.py                   # Memory system for AI assistants
│
├── examples/                   # Educational examples for students
│   └── writing_analysis/       # Extended analysis tools
│       ├── chapter_beats_detection.py
│       ├── chapter_character_dialogue.py
│       ├── chapter_lexical_diversity.py
│       ├── writers_room_v2.py
│       └── ... (7 more analysis tools)
│
├── config/                     # Configuration files
│   ├── mcp_server_config.yaml
│   ├── api_server_config.yaml
│   └── claude_desktop_config.json
│
├── tests/                      # Test suite
│   ├── test_emotion_arc.py
│   └── ... (comprehensive test coverage)
│
├── docs/                       # Documentation
│   ├── DEPENDENCY_MANAGEMENT.md
│   ├── MCP_DOCKER_GUIDE.md
│   └── ... (10 documentation files)
│
├── scripts/                    # Utility scripts
│   ├── setup_mcp_development.sh
│   ├── start_api_server.sh
│   └── quick_analyze.py
│
├── samples/                    # Example text files
├── output/                     # Analysis results directory
│
├── requirements.txt            # Production dependencies (pinned)
├── requirements-dev.txt        # Development dependencies (pinned)
├── Dockerfile                  # Multi-stage production container
├── Dockerfile.mcp              # MCP-specific container (secured)
├── docker-compose.yml          # Standard deployment
├── docker-compose.mcp.yml      # MCP deployment
├── .dockerignore              # Optimized build context
├── .gitignore                 # Version control exclusions
└── CLAUDE.md                  # Claude Code integration guide
```

## 🔒 Security Features

### Recent Security Improvements (v1.1.0)

1. **Docker Security**
   - Non-root user execution (appuser)
   - Security updates applied during build
   - Minimal attack surface with slim base images

2. **Input Validation**
   - Text sanitization (removes control characters, null bytes)
   - Path traversal protection
   - File size limits (100KB max)
   - Pydantic models with strict validation

3. **Rate Limiting**
   - 60 requests/minute per IP (configurable)
   - Per-endpoint limits available
   - In-memory tracking with automatic cleanup

4. **Dependency Security**
   - All packages pinned to exact versions
   - Regular security scanning in CI/CD
   - Minimal dependency footprint

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=tools --cov-report=html

# Run specific test
pytest tests/test_emotion_arc.py -v

# Lint and format checks
black tools/ --check
flake8 tools/
mypy tools/
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run development servers with hot reload
uvicorn tools.emotion_arc_api_server:app --reload --port 8000
```

### API Documentation

When running the FastAPI server, interactive documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### MCP Integration with Claude Desktop

1. Copy config to Claude Desktop:
```bash
cp config/claude_desktop_config.json ~/Library/Application\ Support/Claude/
```

2. The MCP server will be available in Claude Desktop for emotion analysis tasks

## 📚 For Students and Educators

### Learning Modules

#### Module 1: Core MCP Implementation
- Study `tools/emotion_arc_mcp_server.py` for MCP protocol basics
- Learn async request handling and error management
- Understand tool registration and parameter validation

#### Module 2: REST API Design
- Explore `tools/emotion_arc_api_server.py` for FastAPI patterns
- Learn about OpenAPI documentation
- Practice with rate limiting and CORS

#### Module 3: Text Analysis Techniques
- Core emotion analysis in `chapter_emotion_arc.py`
- Lexicon-based sentiment analysis
- Rolling window calculations for trend detection

#### Module 4: Extended Analysis Tools
Browse `examples/writing_analysis/` for:
- Narrative structure detection
- Character dialogue analysis
- Lexical diversity metrics
- Style and readability assessment

### Project Ideas for Students

1. **Extend Lexicons** - Add genre-specific emotion words
2. **New Analysis Tools** - Create tools for plot analysis, theme detection
3. **Visualization** - Add matplotlib/plotly charts to outputs
4. **Machine Learning** - Integrate transformer models for deeper analysis
5. **Web Interface** - Build a React/Vue frontend for the API

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build optimized production image
docker build -f Dockerfile -t emotion-arc:prod .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your_key \
  --name emotion-arc \
  emotion-arc:prod
```

### Docker Compose Stack

```bash
# Start full stack (API + MCP servers)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📈 CI/CD Pipeline

GitHub Actions automatically:
- Runs tests on Python 3.8-3.11
- Checks code formatting (black, flake8)
- Performs type checking (mypy)
- Builds Docker images
- Runs security scans

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

Areas for contribution:
- Additional analysis algorithms
- Performance optimizations
- Documentation improvements
- Test coverage expansion
- UI/UX enhancements

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for educational purposes at [Your Institution]
- Inspired by computational linguistics research
- Designed for integration with Anthropic's Claude via MCP

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ffa-lab-9/issues)
- **Documentation**: See `/docs` folder
- **Examples**: Check `/examples/writing_analysis`

---

**Version**: 1.1.0  
**Last Updated**: January 2025  
**Status**: Production Ready with Security Enhancements

*Happy analyzing! 📊✨*