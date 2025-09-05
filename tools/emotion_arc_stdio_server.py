#!/usr/bin/env python3
"""
Emotion Arc MCP Server for Claude Desktop
A stdio-based MCP server that provides emotion arc analysis as a tool.
"""

import json
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import chapter_emotion_arc
sys.path.insert(0, str(Path(__file__).parent))
from chapter_emotion_arc import analyze
from emotion_report_generator import generate_emotion_report

# Configure logging to stderr so it doesn't interfere with stdio communication
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('/tmp/mcp_emotion_arc.log')]
)
logger = logging.getLogger(__name__)

class EmotionArcMCPServer:
    """Stdio-based MCP server for emotion arc analysis."""
    
    def __init__(self):
        self.name = "emotion-arc-analyzer"
        self.version = "1.0.0"
        logger.info("Emotion Arc MCP Server initialized")
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method", "")
        request_id = request.get("id")
        
        logger.debug(f"Handling request: {method}")
        
        if method == "initialize":
            return self.handle_initialize(request_id, request)
        elif method == "tools/list":
            return self.handle_list_tools(request_id)
        elif method == "tools/call":
            return self.handle_call_tool(request_id, request.get("params", {}))
        elif method == "prompts/list":
            return self.handle_list_prompts(request_id)
        elif method == "resources/list":
            return self.handle_list_resources(request_id)
        elif method == "notifications/initialized":
            return self.handle_initialized_notification()
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"status": "pong"}}
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def handle_initialize(self, request_id: Any, request: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle initialization request."""
        # Get the client's protocol version from request params
        if request is None:
            request = {}
        params = request.get("params", {})
        client_protocol = params.get("protocolVersion", "2025-06-18")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": client_protocol,  # Echo back client's protocol version
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }
    
    def handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """List available tools."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "analyze_emotion_arc",
                        "description": "Analyze the emotional arc of a text using sentiment and emotion lexicons",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The text to analyze"
                                },
                                "window_size": {
                                    "type": "integer",
                                    "description": "Rolling window size for smoothing (default: 5)",
                                    "default": 5,
                                    "minimum": 1,
                                    "maximum": 50
                                },
                                "output_format": {
                                    "type": "string",
                                    "description": "Output format: 'json' for data or 'report' for formatted markdown report (default: report)",
                                    "enum": ["json", "report"],
                                    "default": "report"
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "Optional filename for the report header (default: 'text')",
                                    "default": "text"
                                }
                            },
                            "required": ["text"]
                        }
                    }
                ]
            }
        }
    
    def handle_list_prompts(self, request_id: Any) -> Dict[str, Any]:
        """List available prompts (none for this server)."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": []
            }
        }
    
    def handle_list_resources(self, request_id: Any) -> Dict[str, Any]:
        """List available resources (none for this server)."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []
            }
        }
    
    def handle_initialized_notification(self) -> None:
        """Handle initialized notification (no response needed for notifications)."""
        logger.debug("Received initialized notification")
        return None  # Notifications don't get responses
    
    def handle_call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.debug(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        if tool_name == "analyze_emotion_arc":
            try:
                text = arguments.get("text", "")
                window_size = arguments.get("window_size", 5)
                
                if not text:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: text is required"
                        }
                    }
                
                # Get additional parameters
                output_format = arguments.get("output_format", "report")
                filename = arguments.get("filename", "text")
                
                # Perform analysis
                scores, val_roll, emo_roll, summary = analyze(text, window_size)
                
                # Format the result based on output_format
                if output_format == "report":
                    # Generate formatted markdown report
                    report = generate_emotion_report(filename, scores, val_roll, emo_roll, summary, window_size)
                    formatted_result = report
                else:
                    # Return JSON data
                    formatted_result = {
                        "summary": {
                            "sentences": summary.sentences,
                            "avg_valence": summary.avg_valence,
                            "top_emotions": summary.top_emotions
                        },
                        "valence_progression": val_roll[:15],  # First 15 values
                        "dominant_emotions": {
                            emotion: values[:15] 
                            for emotion, values in list(emo_roll.items())[:5]
                        },
                        "analysis_parameters": {
                            "window_size": window_size,
                            "text_length": len(text),
                            "sentences_analyzed": len(scores)
                        }
                    }
                    formatted_result = json.dumps(formatted_result, indent=2)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": formatted_result
                            }
                        ]
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in analyze_emotion_arc: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            }
        }
    
    def run(self):
        """Run the stdio server."""
        logger.info("Starting Emotion Arc MCP Server (stdio mode)")
        print("MCP Server starting up", file=sys.stderr, flush=True)
        
        try:
            while True:
                try:
                    # Read from stdin
                    line = sys.stdin.readline()
                    if not line:
                        logger.info("EOF reached, server shutting down")
                        break
                    
                    # Skip empty lines
                    line = line.strip()
                    if not line:
                        continue
                    
                    logger.debug(f"Raw input: {line}")
                    
                    # Parse JSON-RPC request
                    try:
                        request = json.loads(line)
                        logger.debug(f"Received request: {request}")
                        print(f"Processing request: {request.get('method')}", file=sys.stderr, flush=True)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        print(f"JSON decode error: {e}", file=sys.stderr, flush=True)
                        continue
                    
                    # Handle the request
                    response = self.handle_request(request)
                    
                    # Only send response if one is returned (notifications return None)
                    if response is not None:
                        print(f"Sending response for: {request.get('method')}", file=sys.stderr, flush=True)
                        
                        # Send response
                        response_json = json.dumps(response)
                        sys.stdout.write(response_json + '\n')
                        sys.stdout.flush()
                        logger.debug(f"Sent response: {response_json}")
                    else:
                        print(f"No response needed for: {request.get('method')}", file=sys.stderr, flush=True)
                    
                except KeyboardInterrupt:
                    logger.info("Server interrupted by user")
                    break
                except EOFError:
                    logger.info("EOF on stdin, server shutting down")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    # Send error response if we have a request id
                    try:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32603,
                                "message": f"Internal error: {str(e)}"
                            }
                        }
                        sys.stdout.write(json.dumps(error_response) + '\n')
                        sys.stdout.flush()
                    except:
                        logger.error("Failed to send error response")
                    
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        finally:
            logger.info("Server shutting down")

if __name__ == "__main__":
    server = EmotionArcMCPServer()
    server.run()