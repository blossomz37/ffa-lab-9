#!/usr/bin/env python3
"""
Test the MCP server locally to ensure it works before Claude Desktop connection.
"""

import json
import subprocess
import time

def test_mcp_server():
    """Test the MCP server with basic requests."""
    
    print("🧪 Testing Emotion Arc MCP Server")
    print("=" * 50)
    
    # Start the server process
    cmd = ["python3", "/Users/carlo/Lab-9/tools/emotion_arc_stdio_server.py"]
    env = {"PYTHONPATH": "/Users/carlo/Lab-9"}
    
    try:
        # Test request 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        print("\n1️⃣ Testing initialize...")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send initialize request
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        response = proc.stdout.readline()
        if response:
            result = json.loads(response)
            print("✅ Initialize response received:")
            print(f"   Server: {result.get('result', {}).get('serverInfo', {}).get('name')}")
            print(f"   Version: {result.get('result', {}).get('serverInfo', {}).get('version')}")
        
        # Test request 2: List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n2️⃣ Testing tools/list...")
        proc.stdin.write(json.dumps(list_request) + "\n")
        proc.stdin.flush()
        
        response = proc.stdout.readline()
        if response:
            result = json.loads(response)
            tools = result.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Test request 3: Call tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "analyze_emotion_arc",
                "arguments": {
                    "text": "I was happy and excited. Then fear crept in. But hope returned.",
                    "window_size": 2
                }
            }
        }
        
        print("\n3️⃣ Testing tool call...")
        proc.stdin.write(json.dumps(call_request) + "\n")
        proc.stdin.flush()
        
        response = proc.stdout.readline()
        if response:
            result = json.loads(response)
            if 'result' in result:
                print("✅ Analysis completed successfully!")
                content = result['result']['content'][0]['text']
                analysis = json.loads(content)
                print(f"   Sentences analyzed: {analysis['summary']['sentences']}")
                print(f"   Average valence: {analysis['summary']['avg_valence']:.2f}")
            elif 'error' in result:
                print(f"❌ Error: {result['error']['message']}")
        
        # Terminate the process
        proc.terminate()
        proc.wait(timeout=5)
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! MCP server is ready.")
        print("\n📝 Next steps:")
        print("1. Restart Claude Desktop")
        print("2. In a new chat, type: 'Use the emotion-arc-analyzer tool'")
        print("3. Or ask: 'Analyze the emotional arc of this text: [your text]'")
        
    except subprocess.TimeoutExpired:
        print("❌ Server process timed out")
        proc.kill()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Make sure all dependencies are installed:")
        print("   pip install pydantic fastapi")

if __name__ == "__main__":
    test_mcp_server()