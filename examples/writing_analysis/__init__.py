"""
Extended writing analysis tools for educational purposes.
"""

# Import core dependencies from tools package
import sys
from pathlib import Path

# Add parent directories to path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Now we can import from tools
from tools.chapter_emotion_arc import analyze, sentences, tokens

__all__ = ['analyze', 'sentences', 'tokens']