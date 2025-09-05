#!/usr/bin/env python3
"""
Test MCP server report generation
"""

import json
import subprocess

def test_report_generation():
    """Test the MCP server's report generation capability."""
    
    cmd = ["python3", "/Users/carlo/Lab-9/tools/emotion_arc_stdio_server.py"]
    env = {"PYTHONPATH": "/Users/carlo/Lab-9"}
    
    # Test text with clear emotional content
    test_text = """The darkness crept through the abandoned hallway, filling Sarah with dread and terror. 
    Her trembling hands clutched the flashlight as shadows danced menacingly around her.
    But then, a warm light appeared ahead, bringing hope and relief to her frightened heart.
    Joy flooded through her as she realized she had found the exit."""
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        proc.stdout.readline()  # consume response
        
        # Test report generation
        report_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "analyze_emotion_arc",
                "arguments": {
                    "text": test_text,
                    "window_size": 2,
                    "output_format": "report",
                    "filename": "Chapter_1.md"
                }
            }
        }
        
        print("🧪 Testing report generation...")
        proc.stdin.write(json.dumps(report_request) + "\n")
        proc.stdin.flush()
        
        response = proc.stdout.readline()
        if response:
            result = json.loads(response)
            if 'result' in result:
                report_text = result['result']['content'][0]['text']
                print("✅ Report generated successfully!")
                print("\n" + "="*50)
                print(report_text)
                print("="*50)
                return True
            else:
                print(f"❌ Error in result: {result}")
                return False
        
        proc.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n✅ MCP server report generation is working!")
    else:
        print("\n❌ MCP server report generation failed!")