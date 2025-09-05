#!/bin/bash

# Start MCP and API servers with Docker
set -e

echo "🚀 Starting MCP and API Servers with Docker"
echo "==========================================="

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Parse command line arguments
SERVICE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --mcp)
            SERVICE="mcp-server"
            shift
            ;;
        --api)
            SERVICE="api"
            shift
            ;;
        --all)
            SERVICE=""
            shift
            ;;
        --stop)
            echo "🛑 Stopping all services..."
            docker compose -f docker-compose.mcp.yml down
            exit 0
            ;;
        --logs)
            docker compose -f docker-compose.mcp.yml logs -f
            exit 0
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --mcp     Start only the MCP server"
            echo "  --api     Start only the API server"
            echo "  --all     Start all services (default)"
            echo "  --stop    Stop all services"
            echo "  --logs    Show logs from all services"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build the Docker image
echo "📦 Building Docker image..."
docker compose -f docker-compose.mcp.yml build

# Start services
if [ -z "$SERVICE" ]; then
    echo "🔧 Starting all services..."
    docker compose -f docker-compose.mcp.yml up -d
    
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "📡 Available endpoints:"
    echo "   MCP Server: http://localhost:9000"
    echo "   API Server: http://localhost:8000"
    echo "   API Docs:   http://localhost:8000/docs"
    echo "   Health:     http://localhost:8000/health"
    echo ""
    echo "💡 To view logs: ./scripts/start_mcp_docker.sh --logs"
    echo "🛑 To stop:      ./scripts/start_mcp_docker.sh --stop"
else
    echo "🔧 Starting $SERVICE..."
    docker compose -f docker-compose.mcp.yml up -d $SERVICE
    
    echo ""
    echo "✅ $SERVICE started successfully!"
fi

# Wait a moment for services to start
sleep 2

# Check service health
echo ""
echo "🏥 Checking service health..."

if [ -z "$SERVICE" ] || [ "$SERVICE" = "api" ]; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API Server is healthy"
    else
        echo "⚠️  API Server is not responding yet (may still be starting)"
    fi
fi

if [ -z "$SERVICE" ] || [ "$SERVICE" = "mcp-server" ]; then
    if docker compose -f docker-compose.mcp.yml ps mcp-server | grep -q "Up"; then
        echo "✅ MCP Server is running"
    else
        echo "⚠️  MCP Server is not running yet"
    fi
fi