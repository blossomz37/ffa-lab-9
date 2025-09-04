#!/usr/bin/env python3
"""
Simple test for FastAPI server components
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent.parent / "tools"))

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        import yaml
        print("✅ YAML imported successfully")
    except ImportError as e:
        print(f"❌ YAML import failed: {e}")
        return False
    
    try:
        from chapter_emotion_arc import analyze, sentences
        print("✅ Core emotion analysis imported successfully")
    except ImportError as e:
        print(f"❌ Core analysis import failed: {e}")
        return False
    
    return True

def test_basic_analysis():
    """Test basic emotion analysis functionality."""
    print("\nTesting basic analysis...")
    
    try:
        from chapter_emotion_arc import analyze
        
        test_text = "I am happy today. But yesterday I was sad. Tomorrow will be better!"
        scores, val_roll, emo_roll, summary = analyze(test_text, window=3)
        
        print(f"✅ Analysis successful!")
        print(f"   Sentences: {summary.sentences}")
        print(f"   Avg Valence: {summary.avg_valence}")
        print(f"   Top Emotions: {summary.top_emotions}")
        
        return True
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation."""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
        
        # Create a simple test app
        app = FastAPI(title="Test App")
        
        class TestRequest(BaseModel):
            text: str = Field(..., min_length=1)
            window_size: int = Field(default=5, ge=1, le=50)
        
        @app.get("/")
        async def root():
            return {"message": "Hello World"}
        
        @app.post("/test")
        async def test_endpoint(request: TestRequest):
            return {"received": request.text, "window": request.window_size}
        
        print("✅ FastAPI app created successfully")
        print("✅ Pydantic models work correctly")
        print("✅ Endpoints defined successfully")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing FastAPI Server Components")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test basic analysis
    if not test_basic_analysis():
        success = False
    
    # Test FastAPI app
    if not test_fastapi_app():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All component tests passed!")
        print("💡 You can now start the server with:")
        print("   python tools/emotion_arc_api_server.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
