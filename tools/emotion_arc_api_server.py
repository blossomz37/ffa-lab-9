#!/usr/bin/env python3
"""
emotion_arc_api_server.py
------------------------
FastAPI-based HTTP API server for emotion arc analysis.
This is the fallback implementation that provides the same functionality
as the MCP server but using standard HTTP API endpoints.

USAGE:
    python tools/emotion_arc_api_server.py
    
    Or with configuration:
    python tools/emotion_arc_api_server.py --config config/api_server_config.yaml

REQUIREMENTS:
    pip install fastapi uvicorn pydantic

This educational implementation demonstrates:
- RESTful API design
- Async request handling
- Input validation with Pydantic
- Multiple output formats
- OpenAPI/Swagger documentation
- CORS support for web integration
"""

import asyncio
import json
import logging
import argparse
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, ValidationError
import uvicorn

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

# Pydantic models for request/response validation
class EmotionArcRequest(BaseModel):
    """Request model for emotion arc analysis."""
    text: str = Field(..., description="Text to analyze for emotional progression", min_length=1)
    window_size: int = Field(default=5, ge=1, le=50, description="Rolling window size for analysis")
    output_format: str = Field(default="json", pattern="^(json|csv|markdown)$", description="Output format")
    include_sentences: bool = Field(default=False, description="Include individual sentence analysis")

class EmotionArcSummary(BaseModel):
    """Summary statistics from emotion analysis."""
    sentences: int
    avg_valence: float
    top_emotions: List[str]

class EmotionArcResult(BaseModel):
    """Complete emotion arc analysis result."""
    summary: EmotionArcSummary
    valence_rolling: List[float]
    emotions_rolling: Dict[str, List[float]]
    parameters: Dict[str, Any]
    metadata: Dict[str, str]
    sentences: Optional[List[Dict[str, Any]]] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    timestamp: str

# Emotion Arc Analyzer Class
class EmotionArcAnalyzer:
    """Wrapper class for the emotion arc analysis functionality."""
    
    def __init__(self, max_text_length: int = 100000):
        self.max_text_length = max_text_length
        self.version = "1.0.0"
        
    async def analyze_text(self, request: EmotionArcRequest) -> EmotionArcResult:
        """
        Analyze text for emotional progression.
        
        Args:
            request: Validated request containing text and parameters
            
        Returns:
            EmotionArcResult containing analysis results
            
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
            
            # Convert summary to Pydantic model
            summary_model = EmotionArcSummary(
                sentences=summary.sentences,
                avg_valence=summary.avg_valence,
                top_emotions=summary.top_emotions
            )
            
            # Build result
            result = EmotionArcResult(
                summary=summary_model,
                valence_rolling=val_roll,
                emotions_rolling=emo_roll,
                parameters={
                    "window_size": request.window_size,
                    "text_length": len(request.text),
                    "sentence_count": len(sentences(request.text))
                },
                metadata={
                    "tool_version": self.version,
                    "analysis_method": "lexicon_based",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Include individual sentences if requested
            if request.include_sentences:
                result.sentences = [
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
    
    def format_as_csv(self, result: EmotionArcResult) -> str:
        """Format results as CSV."""
        lines = ["sentence_index,valence_rolling,joy_rolling,sadness_rolling,anger_rolling,fear_rolling,trust_rolling,disgust_rolling,surprise_rolling,anticipation_rolling"]
        
        val_roll = result.valence_rolling
        emo_roll = result.emotions_rolling
        emotions = ["joy", "sadness", "anger", "fear", "trust", "disgust", "surprise", "anticipation"]
        
        for i in range(len(val_roll)):
            row = [str(i), f"{val_roll[i]:.3f}"]
            for emotion in emotions:
                row.append(f"{emo_roll[emotion][i]:.3f}")
            lines.append(",".join(row))
        
        return "\n".join(lines)
    
    def format_as_markdown(self, result: EmotionArcResult) -> str:
        """Format results as Markdown report."""
        summary = result.summary
        params = result.parameters
        
        md = f"""# Emotion Arc Analysis Report

## Summary
- **Sentences**: {summary.sentences}
- **Average Valence**: {summary.avg_valence}
- **Top Emotions**: {', '.join(summary.top_emotions)}
- **Window Size**: {params['window_size']}

## Analysis Parameters
- Text Length: {params['text_length']} characters
- Sentence Count: {params['sentence_count']}
- Analysis Method: {result.metadata['analysis_method']}
- Timestamp: {result.metadata['timestamp']}

## Key Insights
The text shows an overall {'positive' if summary.avg_valence > 0 else 'negative' if summary.avg_valence < 0 else 'neutral'} emotional tone.
The dominant emotions are: {', '.join(summary.top_emotions[:3])}.

## Rolling Window Analysis
The analysis used a rolling window of {params['window_size']} sentences to smooth emotional fluctuations and identify overall trends.

---
*Generated by FFA Lab 9 Emotion Arc Analyzer API Server*
"""
        return md

# Initialize FastAPI app and analyzer
app = FastAPI(
    title="Emotion Arc Analysis API",
    description="Educational API for analyzing emotional progression in text using sentiment lexicons",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web client support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = EmotionArcAnalyzer()

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "Emotion Arc Analysis API",
        "version": "1.0.0",
        "description": "Educational API for analyzing emotional progression in text",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=analyzer.version
    )

@app.post("/analyze", response_model=EmotionArcResult)
async def analyze_emotion_arc(
    request: EmotionArcRequest = Body(..., description="Analysis request parameters")
):
    """
    Analyze text for emotional progression.
    
    This endpoint accepts text and returns a detailed analysis of emotional
    progression using sentiment lexicons and rolling averages.
    """
    try:
        result = await analyzer.analyze_text(request)
        return result
    except ValueError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze/csv")
async def analyze_emotion_arc_csv(
    request: EmotionArcRequest = Body(..., description="Analysis request parameters")
):
    """
    Analyze text and return results in CSV format.
    """
    try:
        # Force CSV format
        request.output_format = "csv"
        result = await analyzer.analyze_text(request)
        csv_output = analyzer.format_as_csv(result)
        
        return PlainTextResponse(
            content=csv_output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=emotion_analysis.csv"}
        )
    except ValueError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze/markdown")
async def analyze_emotion_arc_markdown(
    request: EmotionArcRequest = Body(..., description="Analysis request parameters")
):
    """
    Analyze text and return results in Markdown format.
    """
    try:
        # Force Markdown format
        request.output_format = "markdown"
        result = await analyzer.analyze_text(request)
        markdown_output = analyzer.format_as_markdown(result)
        
        return PlainTextResponse(
            content=markdown_output,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=emotion_analysis.md"}
        )
    except ValueError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analyze/quick")
async def quick_analyze(
    text: str = Query(..., description="Text to analyze", min_length=1),
    window_size: int = Query(5, ge=1, le=50, description="Rolling window size"),
    include_sentences: bool = Query(False, description="Include sentence details")
):
    """
    Quick analysis endpoint using URL parameters.
    Useful for simple GET requests and testing.
    """
    try:
        request = EmotionArcRequest(
            text=text,
            window_size=window_size,
            include_sentences=include_sentences
        )
        result = await analyzer.analyze_text(request)
        return result
    except ValueError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            detail=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Configuration loading
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    default_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8000,
            "debug": False,
            "reload": False
        },
        "analysis": {
            "max_text_length": 100000,
            "default_window_size": 5
        },
        "logging": {
            "level": "INFO"
        }
    }
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                # Merge configurations
                for key, value in file_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    return default_config

def main():
    """Main server entry point."""
    parser = argparse.ArgumentParser(description="FastAPI Server for Emotion Arc Analysis")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (optional)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    host = args.host or config["server"]["host"]
    port = args.port or config["server"]["port"]
    reload = args.reload or config["server"].get("reload", False)
    
    # Configure analyzer with config settings
    global analyzer
    max_length = config["analysis"].get("max_text_length", 100000)
    analyzer = EmotionArcAnalyzer(max_text_length=max_length)
    
    # Configure logging
    log_level = config["logging"].get("level", "INFO")
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    logger.info(f"Starting Emotion Arc Analysis API Server")
    logger.info(f"Server will be available at: http://{host}:{port}")
    logger.info(f"API documentation: http://{host}:{port}/docs")
    logger.info(f"Health check: http://{host}:{port}/health")
    
    # Run the server
    uvicorn.run(
        "emotion_arc_api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower()
    )

if __name__ == "__main__":
    main()
