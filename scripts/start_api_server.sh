#!/bin/bash

# start_api_server.sh
# Convenient script to start the FastAPI Emotion Arc Analyzer server

set -e  # Exit on any error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting FastAPI Emotion Arc Analysis Server"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Virtual environment not found. Running setup first..."
    cd "$PROJECT_ROOT"
    ./scripts/setup_mcp_development.sh
fi

# Activate virtual environment
cd "$PROJECT_ROOT"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing FastAPI dependencies..."
    pip install fastapi uvicorn
fi

echo "✅ Environment ready"

# Parse command line arguments
CONFIG_FILE=""
HOST="127.0.0.1"
PORT="8000"
RELOAD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --reload)
            RELOAD="--reload"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --config FILE    Configuration file path"
            echo "  --host HOST      Host to bind to (default: 127.0.0.1)"
            echo "  --port PORT      Port to bind to (default: 8000)"
            echo "  --reload         Enable auto-reload for development"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python tools/emotion_arc_api_server.py --host $HOST --port $PORT"

if [ -n "$CONFIG_FILE" ]; then
    CMD="$CMD --config $CONFIG_FILE"
fi

if [ -n "$RELOAD" ]; then
    CMD="$CMD $RELOAD"
fi

echo "🌐 Server will be available at: http://$HOST:$PORT"
echo "📖 API documentation: http://$HOST:$PORT/docs"
echo "🔍 Interactive API: http://$HOST:$PORT/redoc"
echo ""
echo "💡 Useful endpoints:"
echo "   Health check: GET http://$HOST:$PORT/health"
echo "   Analyze text: POST http://$HOST:$PORT/analyze"
echo "   Quick analyze: GET http://$HOST:$PORT/analyze/quick?text=your+text+here"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server
echo "Starting server with: $CMD"
exec $CMD
