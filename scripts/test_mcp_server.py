#!/usr/bin/env python3
"""
test_mcp_server.py
-----------------
Test script for the MCP Emotion Arc Analyzer server.
This script helps verify that the MCP server implementation works correctly.

USAGE:
    python scripts/test_mcp_server.py
    
    Or with custom test text:
    python scripts/test_mcp_server.py --text "Your custom text here"
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add tools directory to path
sys.path.append(str(Path(__file__).parent.parent / "tools"))

try:
    from emotion_arc_mcp_server import EmotionArcAnalyzer, EmotionArcRequest
    print("✅ Successfully imported MCP server components")
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print("💡 Make sure you've installed dependencies: pip install mcp pydantic")
    sys.exit(1)

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

async def test_analysis(text: str, window_size: int = 5, output_format: str = "json") -> Dict[str, Any]:
    """Test the emotion analysis with given parameters."""
    analyzer = EmotionArcAnalyzer()
    
    request = EmotionArcRequest(
        text=text,
        window_size=window_size,
        output_format=output_format,
        include_sentences=True
    )
    
    try:
        result = await analyzer.analyze_text(request)
        return {
            "status": "success",
            "result": result,
            "formatted": analyzer.format_output(result, output_format)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def run_test_suite():
    """Run comprehensive test suite."""
    print("🧪 Running MCP Server Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Simple text analysis
    print("\n📝 Test 1: Simple Text Analysis")
    tests_total += 1
    result = await test_analysis(SAMPLE_TEXTS["simple"], window_size=3)
    if result["status"] == "success":
        print("✅ PASSED")
        summary = result["result"]["summary"]
        print(f"   Sentences: {summary['sentences']}")
        print(f"   Avg Valence: {summary['avg_valence']}")
        print(f"   Top Emotions: {summary['top_emotions']}")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Test 2: Complex text with different window sizes
    print("\n📚 Test 2: Complex Text with Different Window Sizes")
    for window in [3, 5, 7]:
        tests_total += 1
        result = await test_analysis(SAMPLE_TEXTS["complex"], window_size=window)
        if result["status"] == "success":
            print(f"✅ PASSED (window={window})")
            tests_passed += 1
        else:
            print(f"❌ FAILED (window={window}): {result['error']}")
    
    # Test 3: Different output formats
    print("\n📊 Test 3: Output Format Testing")
    for format_type in ["json", "csv", "markdown"]:
        tests_total += 1
        result = await test_analysis(SAMPLE_TEXTS["emotional_journey"], 
                                   window_size=4, output_format=format_type)
        if result["status"] == "success":
            print(f"✅ PASSED ({format_type} format)")
            if format_type == "markdown":
                print("   Sample output:")
                lines = result["formatted"].split('\n')[:5]
                for line in lines:
                    print(f"   {line}")
                print("   ...")
            tests_passed += 1
        else:
            print(f"❌ FAILED ({format_type} format): {result['error']}")
    
    # Test 4: Edge cases
    print("\n⚠️  Test 4: Edge Cases")
    
    # Empty text
    tests_total += 1
    result = await test_analysis("", window_size=5)
    if result["status"] == "error":
        print("✅ PASSED (empty text handling)")
        tests_passed += 1
    else:
        print("❌ FAILED (should reject empty text)")
    
    # Very long text
    tests_total += 1
    long_text = "I am happy. " * 10000  # About 120,000 characters
    result = await test_analysis(long_text, window_size=5)
    if result["status"] == "error":
        print("✅ PASSED (long text handling)")
        tests_passed += 1
    else:
        print("❌ FAILED (should reject overly long text)")
    
    # Invalid window size
    tests_total += 1
    try:
        request = EmotionArcRequest(
            text="Test text",
            window_size=100,  # Should be rejected (max 50)
            output_format="json"
        )
        print("❌ FAILED (should reject invalid window size)")
    except Exception:
        print("✅ PASSED (invalid window size handling)")
        tests_passed += 1
    
    # Test 5: Neutral text
    print("\n😐 Test 5: Neutral Text Analysis")
    tests_total += 1
    result = await test_analysis(SAMPLE_TEXTS["neutral"], window_size=5)
    if result["status"] == "success":
        print("✅ PASSED")
        summary = result["result"]["summary"]
        print(f"   Valence: {summary['avg_valence']} (should be near 0)")
        tests_passed += 1
    else:
        print(f"❌ FAILED: {result['error']}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! MCP server is ready.")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Check implementation.")
        return False

async def interactive_test():
    """Run interactive testing mode."""
    print("\n🎮 Interactive Testing Mode")
    print("Enter text to analyze (or 'quit' to exit):")
    
    analyzer = EmotionArcAnalyzer()
    
    while True:
        try:
            text = input("\n> ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                print("Please enter some text to analyze.")
                continue
            
            # Get parameters
            window = input("Window size (default 5): ").strip()
            window = int(window) if window.isdigit() else 5
            
            format_type = input("Output format (json/csv/markdown, default json): ").strip()
            format_type = format_type if format_type in ["json", "csv", "markdown"] else "json"
            
            # Run analysis
            result = await test_analysis(text, window_size=window, output_format=format_type)
            
            if result["status"] == "success":
                print("\n📊 Analysis Results:")
                summary = result["result"]["summary"]
                print(f"• Sentences: {summary['sentences']}")
                print(f"• Average Valence: {summary['avg_valence']}")
                print(f"• Top Emotions: {summary['top_emotions']}")
                
                if format_type != "json":
                    print(f"\n📝 Formatted Output ({format_type}):")
                    print(result["formatted"][:500] + "..." if len(result["formatted"]) > 500 else result["formatted"])
            else:
                print(f"❌ Error: {result['error']}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\nGoodbye! 👋")

async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP Emotion Arc Server")
    parser.add_argument("--text", type=str, help="Custom text to analyze")
    parser.add_argument("--interactive", action="store_true", help="Run interactive testing mode")
    parser.add_argument("--window", type=int, default=5, help="Window size for analysis")
    parser.add_argument("--format", type=str, default="json", choices=["json", "csv", "markdown"],
                      help="Output format")
    
    args = parser.parse_args()
    
    if args.text:
        # Single text analysis
        print(f"🔍 Analyzing custom text with window size {args.window}")
        result = await test_analysis(args.text, window_size=args.window, output_format=args.format)
        
        if result["status"] == "success":
            print("✅ Analysis successful!")
            print("\n📊 Results:")
            print(result["formatted"])
        else:
            print(f"❌ Analysis failed: {result['error']}")
    
    elif args.interactive:
        # Interactive mode
        await interactive_test()
    
    else:
        # Run full test suite
        success = await run_test_suite()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
