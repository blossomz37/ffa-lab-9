"""
Core MCP and emotion analysis tools.
"""

from .chapter_emotion_arc import analyze, sentences, tokens, score_sentence
from .memory_mcp import MemoryTool

__all__ = [
    'analyze',
    'sentences', 
    'tokens',
    'score_sentence',
    'MemoryTool'
]

__version__ = '1.0.0'