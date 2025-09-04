#!/usr/bin/env python3
"""
test_api_server.py
-----------------
Test script for the FastAPI Emotion Arc Analyzer server.
This script helps verify that the API server works correctly.

USAGE:
    python scripts/test_api_server.py
    
    Or with specific tests:
    python scripts/test_api_server.py --endpoint analyze --text "Your text here"
"""

import asyncio
import json
import sys
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Test data
SAMPLE_TEXTS = {
    "simple": "I am happy today. But yesterday I was sad. Tomorrow will be better!",
    "complex": """
    The morning sun broke through the clouds, filling Sarah with joy and anticipation. 
    She had been waiting for this day for months, dreaming of the possibilities that lay ahead.
    
    However, as she approached the towering glass building, a wave of anxiety washed over her. 
    What if things didn't go as planned? The uncertainty was almost overwhelming, making her 
    stomach churn with nervous energy.
    
    But then she remembered her friend's encouraging words from the night before: "You've got this!"
    Taking a deep breath, she pushed through her fears and stepped through the revolving door.
    The warmth of the reception area immediately calmed her nerves. 
    
    This was going to be a good day after all. She could feel it in her bones.
    """,
    "neutral": "The weather report shows partly cloudy skies. Temperature will reach 72 degrees. Wind speed is 5 mph from the northeast.",
    "emotional_journey": """
    At first, everything seemed perfect. The garden was in full bloom, birds singing their morning songs.
    Then the storm clouds gathered, dark and menacing. Fear crept into her heart as thunder rumbled overhead.
    The rain came suddenly, washing away her carefully planted flowers. Anger and frustration overwhelmed her.
    But as the storm passed, she noticed something beautiful - the rain had revealed a hidden spring.
    Wonder and gratitude filled her soul. Sometimes destruction leads to discovery.
    """
}

class APITester:
    """Test client for the Emotion Arc API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health(self) -> Dict[str, Any]:
        """Test the health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {"status": "success", "result": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_root(self) -> Dict[str, Any]:
        """Test the root endpoint."""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return {"status": "success", "result": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_analyze(self, text: str, window_size: int = 5, include_sentences: bool = False) -> Dict[str, Any]:
        """Test the main analyze endpoint."""
        try:
            payload = {
                "text": text,
                "window_size": window_size,
                "include_sentences": include_sentences
            }
            response = self.session.post(f"{self.base_url}/analyze", json=payload)
            response.raise_for_status()
            return {"status": "success", "result": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_analyze_csv(self, text: str, window_size: int = 5) -> Dict[str, Any]:
        """Test the CSV output endpoint."""
        try:
            payload = {
                "text": text,
                "window_size": window_size
            }
            response = self.session.post(f"{self.base_url}/analyze/csv", json=payload)
            response.raise_for_status()
            return {"status": "success", "result": response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_analyze_markdown(self, text: str, window_size: int = 5) -> Dict[str, Any]:
        """Test the Markdown output endpoint."""
        try:
            payload = {
                "text": text,
                "window_size": window_size
            }
            response = self.session.post(f"{self.base_url}/analyze/markdown", json=payload)
            response.raise_for_status()
            return {"status": "success", "result": response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_quick_analyze(self, text: str, window_size: int = 5) -> Dict[str, Any]:
        """Test the quick analyze GET endpoint."""
        try:
            params = {
                "text": text,
                "window_size": window_size
            }
            response = self.session.get(f"{self.base_url}/analyze/quick", params=params)
            response.raise_for_status()
            return {"status": "success", "result": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def wait_for_server(base_url: str = "http://127.0.0.1:8000", timeout: int = 30) -> bool:
    """Wait for the server to be ready."""
    print(f"⏳ Waiting for server at {base_url}...")
    
    for i in range(timeout):
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   Still waiting... ({i}s elapsed)")
    
    print(f"❌ Server not ready after {timeout}s")
    return False

def run_comprehensive_tests():
    """Run comprehensive test suite."""
    print("🧪 Running FastAPI Server Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not wait_for_server():
        print("❌ Server is not running. Please start it first:")
        print("   python tools/emotion_arc_api_server.py")
        return False
    
    tester = APITester()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    print("\n🩺 Test 1: Health Check")
    tests_total += 1
    result = tester.test_health()
    if result["status"] == "success":
        print("✅ PASSED")
        health_data = result["result"]
        print(f"   Status: {health_data.get('status', 'unknown')}")
        print(f"   Version: {health_data.get('version', 'unknown')}")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 2: Root endpoint
    print("\n🏠 Test 2: Root Endpoint")
    tests_total += 1
    result = tester.test_root()
    if result["status"] == "success":
        print("✅ PASSED")
        root_data = result["result"]
        print(f"   API Name: {root_data.get('name', 'unknown')}")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 3: Main analyze endpoint
    print("\n📝 Test 3: Main Analysis Endpoint")
    tests_total += 1
    result = tester.test_analyze(SAMPLE_TEXTS["simple"], window_size=3, include_sentences=True)
    if result["status"] == "success":
        print("✅ PASSED")
        analysis_data = result["result"]
        summary = analysis_data.get("summary", {})
        print(f"   Sentences: {summary.get('sentences', 'unknown')}")
        print(f"   Avg Valence: {summary.get('avg_valence', 'unknown')}")
        print(f"   Top Emotions: {summary.get('top_emotions', [])}")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 4: CSV output
    print("\n📊 Test 4: CSV Output")
    tests_total += 1
    result = tester.test_analyze_csv(SAMPLE_TEXTS["emotional_journey"], window_size=4)
    if result["status"] == "success":
        print("✅ PASSED")
        csv_lines = result["result"].split('\n')
        print(f"   CSV has {len(csv_lines)} lines")
        print(f"   Header: {csv_lines[0] if csv_lines else 'None'}")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 5: Markdown output
    print("\n📄 Test 5: Markdown Output")
    tests_total += 1
    result = tester.test_analyze_markdown(SAMPLE_TEXTS["complex"], window_size=5)
    if result["status"] == "success":
        print("✅ PASSED")
        markdown_content = result["result"]
        print(f"   Markdown length: {len(markdown_content)} characters")
        if "# Emotion Arc Analysis Report" in markdown_content:
            print("   ✓ Contains proper header")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 6: Quick analyze (GET endpoint)
    print("\n⚡ Test 6: Quick Analyze")
    tests_total += 1
    result = tester.test_quick_analyze(SAMPLE_TEXTS["neutral"], window_size=3)
    if result["status"] == "success":
        print("✅ PASSED")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 7: Error handling
    print("\n⚠️  Test 7: Error Handling")
    tests_total += 1
    result = tester.test_analyze("", window_size=5)  # Empty text should fail
    if result["status"] == "error":
        print("✅ PASSED (correctly rejected empty text)")
        tests_passed += 1
    else:
        print("❌ FAILED (should reject empty text)")
    
    # Test 8: Large window size
    print("\n📏 Test 8: Input Validation")
    tests_total += 1
    result = tester.test_analyze("Test text", window_size=100)  # Should fail (max 50)
    if result["status"] == "error":
        print("✅ PASSED (correctly rejected large window size)")
        tests_passed += 1
    else:
        print("❌ FAILED (should reject window size > 50)")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! API server is working correctly.")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Check the server.")
        return False

def run_single_test(endpoint: str, text: str, window_size: int = 5):
    """Run a single test."""
    if not wait_for_server():
        print("❌ Server is not running.")
        return
    
    tester = APITester()
    
    print(f"🔍 Testing {endpoint} endpoint...")
    
    if endpoint == "analyze":
        result = tester.test_analyze(text, window_size)
    elif endpoint == "csv":
        result = tester.test_analyze_csv(text, window_size)
    elif endpoint == "markdown":
        result = tester.test_analyze_markdown(text, window_size)
    elif endpoint == "quick":
        result = tester.test_quick_analyze(text, window_size)
    else:
        print(f"❌ Unknown endpoint: {endpoint}")
        return
    
    if result["status"] == "success":
        print("✅ Test successful!")
        if endpoint in ["csv", "markdown"]:
            print("\nResult:")
            print(result["result"][:500] + "..." if len(result["result"]) > 500 else result["result"])
        else:
            print("\nResult:")
            print(json.dumps(result["result"], indent=2)[:1000] + "..." if len(str(result["result"])) > 1000 else json.dumps(result["result"], indent=2))
    else:
        print(f"❌ Test failed: {result['error']}")

def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FastAPI Emotion Arc Server")
    parser.add_argument("--endpoint", type=str, choices=["analyze", "csv", "markdown", "quick"],
                      help="Test specific endpoint")
    parser.add_argument("--text", type=str, help="Custom text to analyze")
    parser.add_argument("--window", type=int, default=5, help="Window size for analysis")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8000", help="Server URL")
    
    args = parser.parse_args()
    
    if args.endpoint and args.text:
        # Single endpoint test
        run_single_test(args.endpoint, args.text, args.window)
    else:
        # Comprehensive test suite
        success = run_comprehensive_tests()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
