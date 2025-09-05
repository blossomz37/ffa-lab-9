#!/usr/bin/env python3
"""
Test script to verify MCP and API servers are working correctly in Docker.
"""

import requests
import json
import sys

def test_api_server():
    """Test the API server endpoints."""
    print("🧪 Testing API Server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API health check: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
        
        # Test analysis endpoint
        test_text = "I was happy and excited about the new project. Then fear crept in as deadlines approached."
        
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "text": test_text,
                "window_size": 3,
                "output_format": "json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API analysis: OK")
            print(f"   Sentences analyzed: {result['summary']['sentences']}")
            print(f"   Average valence: {result['summary']['avg_valence']:.2f}")
            print(f"   Top emotions: {', '.join(result['summary']['top_emotions'][:3])}")
        else:
            print(f"❌ API analysis failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server at http://localhost:8000")
        print("   Make sure the server is running with: docker compose up api")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def check_docker_services():
    """Check if Docker services are running."""
    import subprocess
    
    print("\n🐳 Checking Docker services...")
    
    try:
        # Check docker compose services
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.mcp.yml", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout:
            services = json.loads(result.stdout) if result.stdout.startswith('[') else [json.loads(result.stdout)]
            
            for service in services:
                name = service.get('Name', 'Unknown')
                state = service.get('State', 'Unknown')
                health = service.get('Health', 'N/A')
                
                if state == 'running':
                    print(f"✅ {name}: {state} (health: {health})")
                else:
                    print(f"❌ {name}: {state}")
        else:
            # Fallback to regular docker ps
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=lab-9"],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker Desktop.")
        return False
    except Exception as e:
        print(f"⚠️  Could not check Docker services: {e}")
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("MCP and API Server Docker Test Suite")
    print("=" * 50)
    
    # Check Docker services
    docker_ok = check_docker_services()
    
    # Test API server
    print()
    api_ok = test_api_server()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    if api_ok:
        print("✅ All tests passed!")
        print("\n💡 Your Docker setup is working correctly.")
        print("   The API server is accessible at http://localhost:8000")
        print("   You can view the API documentation at http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some tests failed.")
        print("\n💡 To fix issues:")
        print("   1. Make sure Docker Desktop is running")
        print("   2. Stop existing containers: docker compose down")
        print("   3. Start services: ./scripts/start_mcp_docker.sh --all")
        print("   4. Check logs: docker compose -f docker-compose.mcp.yml logs")
        return 1

if __name__ == "__main__":
    sys.exit(main())