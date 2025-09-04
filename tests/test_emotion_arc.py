"""
Test the emotion arc analysis tool.
"""

import unittest
import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

try:
    from chapter_emotion_arc import sentences, tokens, score_sentence, analyze
except ImportError:
    # Skip tests if module not available
    import pytest
    pytest.skip("chapter_emotion_arc module not available", allow_module_level=True)


class TestEmotionArc(unittest.TestCase):
    """Test cases for emotion arc analysis."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_text = """
        John was happy and excited about the meeting.
        Mary felt sad and worried about the news.
        The team was angry about the decision.
        Everyone felt relief after the announcement.
        """
    
    def test_sentence_splitting(self):
        """Test that text is properly split into sentences."""
        result = sentences(self.sample_text)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result, list)
        
    def test_tokenization(self):
        """Test that sentences are properly tokenized."""
        test_sentence = "Hello, world! This is a test."
        result = tokens(test_sentence)
        self.assertIn("hello", result)
        self.assertIn("world", result)
        self.assertIn("test", result)
    
    def test_sentence_scoring(self):
        """Test that sentence scoring works."""
        positive_sentence = "I am happy and joyful today"
        negative_sentence = "I am sad and angry now"
        
        pos_score = score_sentence(0, positive_sentence)
        neg_score = score_sentence(1, negative_sentence)
        
        self.assertGreater(pos_score.valence, 0)
        self.assertLess(neg_score.valence, 0)


if __name__ == '__main__':
    unittest.main()
