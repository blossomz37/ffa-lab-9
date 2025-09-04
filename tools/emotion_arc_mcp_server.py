#!/usr/bin/env python3
"""
emotion_arc_mcp_server.py
------------------------
MCP Server implementation for the emotion arc analysis tool.
This server exposes the chapter_emotion_arc functionality as an MCP tool
that can be used by AI assistants like Claude.

USAGE:
    python tools/emotion_arc_mcp_server.py
    
    Or with configuration:
    python tools/emotion_arc_mcp_server.py --config config/mcp_server_config.yaml

REQUIREMENTS:
    pip install mcp pydantic fastapi uvicorn

This is an educational implementation demonstrating:
- MCP protocol implementation
- Async request handling
- Error management
- Input validation
- Multiple output formats
"""

import asyncio
import json
import logging
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.server import Server
    from mcp.server.models import InitializeResult
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
    )
except ImportError:
    print("❌ MCP package not found. Install with: pip install mcp")
    print("💡 For now, you can run the setup script: ./scripts/setup_mcp_development.sh")
    exit(1)

from pydantic import BaseModel, Field, ValidationError

# Import our existing emotion arc analysis functionality
import sys
sys.path.append(str(Path(__file__).parent))
from chapter_emotion_arc import analyze, sentences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmotionArcRequest(BaseModel):
    """Pydantic model for emotion arc analysis requests."""
    text: str = Field(..., description="Text to analyze for emotional progression")
    window_size: int = Field(default=5, ge=1, le=50, description="Rolling window size for analysis")
    output_format: str = Field(default="json", pattern="^(json|csv|markdown)$", description="Output format")
    include_sentences: bool = Field(default=False, description="Include individual sentence analysis")

class EmotionArcAnalyzer:
    """Wrapper class for the emotion arc analysis functionality."""
    
    def __init__(self, max_text_length: int = 100000):
        self.max_text_length = max_text_length
        
    async def analyze_text(self, request: EmotionArcRequest) -> Dict[str, Any]:
        """
        Analyze text for emotional progression.
        
        Args:
            request: Validated request containing text and parameters
            
        Returns:
            Dict containing analysis results
            
        Raises:
            ValueError: If text is too long or invalid
        """
        if len(request.text) > self.max_text_length:
            raise ValueError(f"Text too long. Maximum length: {self.max_text_length} characters")
            
        if not request.text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # Use the existing analyze function
            scores, val_roll, emo_roll, summary = analyze(request.text, window=request.window_size)
            
            # Build result dictionary
            result = {
                "summary": asdict(summary),
                "valence_rolling": val_roll,
                "emotions_rolling": emo_roll,
                "parameters": {
                    "window_size": request.window_size,
                    "text_length": len(request.text),
                    "sentence_count": len(sentences(request.text))
                },
                "metadata": {
                    "tool_version": "1.0.0",
                    "analysis_method": "lexicon_based"
                }
            }
            
            # Include individual sentences if requested
            if request.include_sentences:
                result["sentences"] = [
                    {
                        "index": score.index,
                        "text": score.text,
                        "valence_raw": score.valence_raw,
                        "emotions": score.emotions
                    }
                    for score in scores
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise ValueError(f"Analysis failed: {str(e)}")
    
    def format_output(self, result: Dict[str, Any], format_type: str) -> str:
        """Format analysis results according to requested format."""
        if format_type == "json":
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            return self._format_as_csv(result)
        elif format_type == "markdown":
            return self._format_as_markdown(result)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_as_csv(self, result: Dict[str, Any]) -> str:
        """Format results as CSV."""
        lines = ["sentence_index,valence_rolling,joy_rolling,sadness_rolling,anger_rolling,fear_rolling,trust_rolling,disgust_rolling,surprise_rolling,anticipation_rolling"]
        
        val_roll = result["valence_rolling"]
        emo_roll = result["emotions_rolling"]
        emotions = ["joy", "sadness", "anger", "fear", "trust", "disgust", "surprise", "anticipation"]
        
        for i in range(len(val_roll)):
            row = [str(i), f"{val_roll[i]:.3f}"]
            for emotion in emotions:
                row.append(f"{emo_roll[emotion][i]:.3f}")
            lines.append(",".join(row))
        
        return "\n".join(lines)
    
    def _format_as_markdown(self, result: Dict[str, Any]) -> str:
        """Format results as Markdown report."""
        summary = result["summary"]
        params = result["parameters"]
        
        md = f"""# Emotion Arc Analysis Report

## Summary
- **Sentences**: {summary['sentences']}
- **Average Valence**: {summary['avg_valence']}
- **Top Emotions**: {', '.join(summary['top_emotions'])}
- **Window Size**: {params['window_size']}

## Analysis Parameters
- Text Length: {params['text_length']} characters
- Sentence Count: {params['sentence_count']}
- Analysis Method: {result['metadata']['analysis_method']}

## Key Insights
The text shows an overall {'positive' if summary['avg_valence'] > 0 else 'negative' if summary['avg_valence'] < 0 else 'neutral'} emotional tone.
The dominant emotions are: {', '.join(summary['top_emotions'][:3])}.

---
*Generated by FFA Lab 9 MCP Emotion Arc Analyzer*
"""
        return md

# Initialize the MCP server
server = Server("emotion-arc-analyzer")
analyzer = EmotionArcAnalyzer()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Return available tools."""
    return [
        Tool(
            name="analyze_emotion_arc",
            description="Analyze the emotional progression of text using sentiment lexicons and rolling averages",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze for emotional progression"
                    },
                    "window_size": {
                        "type": "integer",
                        "description": "Rolling window size for smoothing (1-50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "csv", "markdown"],
                        "description": "Format for the analysis results",
                        "default": "json"
                    },
                    "include_sentences": {
                        "type": "boolean",
                        "description": "Include individual sentence analysis in results",
                        "default": False
                    }
                },
                "required": ["text"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool execution requests."""
    if name != "analyze_emotion_arc":
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        # Validate input using Pydantic
        request = EmotionArcRequest(**arguments)
        
        # Perform analysis
        result = await analyzer.analyze_text(request)
        
        # Format output
        formatted_output = analyzer.format_output(result, request.output_format)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=formatted_output
                )
            ]
        )
    
    except ValidationError as e:
        error_msg = f"Invalid input parameters: {e}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            isError=True
        )
    
    except ValueError as e:
        error_msg = str(e)
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            isError=True
        )
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            isError=True
        )

async def main():
    """Main server entry point."""
    parser = argparse.ArgumentParser(description="MCP Server for Emotion Arc Analysis")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (optional)"
    )
    args = parser.parse_args()
    
    logger.info("Starting MCP Emotion Arc Analyzer Server")
    logger.info("Server ready to accept connections...")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializeResult(
                protocolVersion="2024-11-05",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                ),
                serverInfo={
                    "name": "emotion-arc-analyzer",
                    "version": "1.0.0"
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
