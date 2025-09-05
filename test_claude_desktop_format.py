#!/usr/bin/env python3
"""
Test MCP server with the exact format Claude Desktop uses.
"""

import json
import subprocess
import sys

def test_claude_format():
    """Test with Claude Desktop's exact request format."""
    
    print("🧪 Testing MCP Server with Claude Desktop Format")
    print("=" * 50)
    
    cmd = ["python3", "/Users/carlo/Lab-9/tools/emotion_arc_stdio_server.py"]
    env = {"PYTHONPATH": "/Users/carlo/Lab-9"}
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Test 1: Initialize with Claude's exact format
        init_request = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "claude-ai",
                    "version": "0.1.0"
                }
            },
            "jsonrpc": "2.0",
            "id": 0
        }
        
        print("1️⃣ Testing initialize (Claude format)...")
        
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        response_line = proc.stdout.readline()
        stderr_output = proc.stderr.readline()
        
        print(f"Stderr: {stderr_output.strip()}")
        
        if response_line:
            try:
                response = json.loads(response_line)
                print("✅ Initialize successful!")
                print(f"   Protocol: {response.get('result', {}).get('protocolVersion')}")
                print(f"   Server: {response.get('result', {}).get('serverInfo', {}).get('name')}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid response JSON: {e}")
                print(f"   Raw response: {response_line}")
        else:
            print("❌ No response received")
        
        # Test 2: List tools
        list_request = {
            "method": "tools/list",
            "params": {},
            "jsonrpc": "2.0",
            "id": 1
        }
        
        print("\n2️⃣ Testing tools/list...")
        
        proc.stdin.write(json.dumps(list_request) + "\n")
        proc.stdin.flush()
        
        response_line = proc.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line)
                tools = response.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools")
                for tool in tools:
                    print(f"   - {tool.get('name')}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid response JSON: {e}")
        
        # Close gracefully
        proc.stdin.close()
        proc.wait(timeout=5)
        
        # Read any remaining stderr
        remaining_stderr = proc.stderr.read()
        if remaining_stderr:
            print(f"\nStderr output: {remaining_stderr}")
        
        print("\n✅ Test completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("❌ Process timed out")
        proc.kill()
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_claude_format()