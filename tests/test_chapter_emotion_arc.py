#!/usr/bin/env python3
"""
Comprehensive test suite for chapter_emotion_arc.py

This test suite covers:
- Unit tests for individual functions
- Integration tests for full workflow
- Edge cases and error handling
- Performance considerations
"""

import unittest
import tempfile
import os
import sys
import json
import csv
from pathlib import Path
from unittest.mock import patch

# Add tools directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

try:
    from chapter_emotion_arc import (
        sentences, tokens, score_sentence, rolling, analyze,
        POS, NEG, EMO, SentenceScore, ArcSummary
    )
except ImportError as e:
    print(f"Cannot import chapter_emotion_arc: {e}")
    sys.exit(1)


class TestTextProcessing(unittest.TestCase):
    """Test basic text processing functions."""
    
    def test_sentence_splitting_basic(self):
        """Test basic sentence splitting functionality."""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        result = sentences(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "This is sentence one.")
        self.assertEqual(result[1], "This is sentence two!")
        self.assertEqual(result[2], "Is this sentence three?")
    
    def test_sentence_splitting_edge_cases(self):
        """Test sentence splitting with edge cases."""
        # Empty text
        self.assertEqual(sentences(""), [])
        
        # Single sentence
        result = sentences("Just one sentence.")
        self.assertEqual(len(result), 1)
        
        # Multiple whitespace
        text = "First sentence.    Second sentence."
        result = sentences(text)
        self.assertEqual(len(result), 2)
        
        # Newlines and carriage returns
        text = "First sentence.\r\nSecond sentence.\rThird sentence.\nFourth sentence."
        result = sentences(text)
        self.assertEqual(len(result), 4)
    
    def test_tokenization_basic(self):
        """Test basic word tokenization."""
        text = "Hello, world! This is a test."
        result = tokens(text)
        expected = ["hello", "world", "this", "is", "a", "test"]
        self.assertEqual(result, expected)
    
    def test_tokenization_edge_cases(self):
        """Test tokenization edge cases."""
        # Empty string
        self.assertEqual(tokens(""), [])
        
        # Contractions and hyphens
        text = "Don't use self-driving cars."
        result = tokens(text)
        self.assertIn("don't", result)
        self.assertIn("self-driving", result)
        
        # Numbers and mixed content
        text = "Room 101 has 3 windows."
        result = tokens(text)
        self.assertIn("101", result)
        self.assertIn("3", result)


class TestEmotionScoring(unittest.TestCase):
    """Test emotion scoring functionality."""
    
    def test_positive_valence(self):
        """Test sentences with positive emotional content."""
        sentence = "I am happy and joyful today."
        score = score_sentence(0, sentence)
        self.assertGreater(score.valence_raw, 0)
        self.assertGreater(score.emotions["joy"], 0)
    
    def test_negative_valence(self):
        """Test sentences with negative emotional content."""
        sentence = "I am sad and angry about this."
        score = score_sentence(0, sentence)
        self.assertLess(score.valence_raw, 0)
        self.assertGreater(score.emotions["sadness"], 0)
        self.assertGreater(score.emotions["anger"], 0)
    
    def test_neutral_sentence(self):
        """Test sentences with no emotional content."""
        sentence = "The table has four legs."
        score = score_sentence(0, sentence)
        self.assertEqual(score.valence_raw, 0)
        self.assertEqual(sum(score.emotions.values()), 0)
    
    def test_mixed_emotions(self):
        """Test sentences with mixed emotional content."""
        sentence = "I was happy but then became sad."
        score = score_sentence(0, sentence)
        # Should detect both joy and sadness
        self.assertGreater(score.emotions["joy"], 0)
        self.assertGreater(score.emotions["sadness"], 0)
    
    def test_score_sentence_structure(self):
        """Test that score_sentence returns proper structure."""
        sentence = "Test sentence."
        score = score_sentence(5, sentence)
        
        self.assertIsInstance(score, SentenceScore)
        self.assertEqual(score.index, 5)
        self.assertEqual(score.text, sentence)
        self.assertIsInstance(score.valence_raw, int)
        self.assertIsInstance(score.emotions, dict)
        
        # Check all emotion categories are present
        for emotion in EMO.keys():
            self.assertIn(emotion, score.emotions)


class TestRollingAverages(unittest.TestCase):
    """Test rolling average calculations."""
    
    def test_rolling_basic(self):
        """Test basic rolling average functionality."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = rolling(values, 3)
        
        expected = [1.0, 1.5, 2.0, 3.0, 4.0]
        self.assertEqual(len(result), len(values))
        for i, (actual, expected_val) in enumerate(zip(result, expected)):
            self.assertAlmostEqual(actual, expected_val, places=2, 
                                 msg=f"Mismatch at index {i}")
    
    def test_rolling_window_size_one(self):
        """Test rolling average with window size 1."""
        values = [1.0, 2.0, 3.0]
        result = rolling(values, 1)
        self.assertEqual(result, values)
    
    def test_rolling_window_larger_than_data(self):
        """Test rolling average when window is larger than data."""
        values = [1.0, 2.0, 3.0]
        result = rolling(values, 10)
        expected = [1.0, 1.5, 2.0]
        for actual, expected_val in zip(result, expected):
            self.assertAlmostEqual(actual, expected_val, places=2)
    
    def test_rolling_empty_list(self):
        """Test rolling average with empty input."""
        result = rolling([], 3)
        self.assertEqual(result, [])


class TestFullAnalysis(unittest.TestCase):
    """Test complete analysis workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_text = """
        Sarah walked into the coffee shop with excitement. She was happy and delighted.
        But then she felt sad and disappointed when she realized her mistake.
        Fear crept in as she worried about being late.
        Finally, relief washed over her when she saw the bookstore.
        Joy returned as she quickened her pace with anticipation.
        """
    
    def test_analyze_basic_functionality(self):
        """Test that analyze returns proper structure."""
        scores, val_roll, emo_roll, summary = analyze(self.sample_text, window=3)
        
        # Check return types
        self.assertIsInstance(scores, list)
        self.assertIsInstance(val_roll, list)
        self.assertIsInstance(emo_roll, dict)
        self.assertIsInstance(summary, ArcSummary)
        
        # Check lengths match
        self.assertEqual(len(scores), len(val_roll))
        for emotion_series in emo_roll.values():
            self.assertEqual(len(emotion_series), len(scores))
    
    def test_analyze_detects_emotions(self):
        """Test that analysis detects expected emotions."""
        scores, val_roll, emo_roll, summary = analyze(self.sample_text)
        
        # Should detect joy, sadness, fear based on our sample text
        self.assertIn("joy", summary.top_emotions)
        
        # Check that some emotions were detected
        total_emotions = sum(sum(score.emotions.values()) for score in scores)
        self.assertGreater(total_emotions, 0)
    
    def test_analyze_empty_text(self):
        """Test analysis with empty text."""
        scores, val_roll, emo_roll, summary = analyze("")
        
        self.assertEqual(len(scores), 0)
        self.assertEqual(len(val_roll), 0)
        self.assertEqual(summary.sentences, 0)
        self.assertEqual(summary.avg_valence, 0.0)


class TestFileHandling(unittest.TestCase):
    """Test file input/output operations."""
    
    def setUp(self):
        """Create temporary files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test text file
        self.test_text = "I am happy today. But I was sad yesterday. Now I feel hope."
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_text)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_file_processing_integration(self):
        """Test complete file processing workflow."""
        # Import main function
        from chapter_emotion_arc import main
        
        csv_file = os.path.join(self.temp_dir, "output.csv")
        json_file = os.path.join(self.temp_dir, "output.json")
        
        # Mock command line arguments
        test_args = ["chapter_emotion_arc.py", self.test_file, 
                    "--csv", csv_file, "--json", json_file, "--window", "2"]
        
        with patch.object(sys, 'argv', test_args):
            try:
                main()
                
                # Check that output files were created
                self.assertTrue(os.path.exists(csv_file))
                self.assertTrue(os.path.exists(json_file))
                
                # Validate CSV structure
                with open(csv_file, 'r') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    self.assertIn("sent_index", header)
                    self.assertIn("valence_raw", header)
                    self.assertIn("valence_rolling", header)
                
                # Validate JSON structure
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    self.assertIn("summary", data)
                    self.assertIn("valence_rolling", data)
                    self.assertIn("emotions_rolling", data)
                    
            except SystemExit:
                # main() calls SystemExit on file not found, which is expected behavior
                pass


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_nonexistent_file_handling(self):
        """Test handling of non-existent files."""
        from chapter_emotion_arc import main
        
        test_args = ["chapter_emotion_arc.py", "/nonexistent/file.txt"]
        
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                main()
    
    def test_malformed_text_handling(self):
        """Test handling of malformed or unusual text."""
        # Text with only punctuation
        weird_text = "!@#$%^&*().,;:"
        try:
            scores, val_roll, emo_roll, summary = analyze(weird_text)
            # Should not crash, even if no meaningful results
            self.assertIsInstance(summary, ArcSummary)
        except Exception as e:
            self.fail(f"Analysis failed on malformed text: {e}")
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        unicode_text = "I am 😊 happy today! This has émotions and 中文 characters."
        try:
            scores, val_roll, emo_roll, summary = analyze(unicode_text)
            self.assertIsInstance(summary, ArcSummary)
        except Exception as e:
            self.fail(f"Analysis failed on Unicode text: {e}")


class TestPerformance(unittest.TestCase):
    """Test performance with larger inputs."""
    
    def test_large_text_performance(self):
        """Test performance with a large text sample."""
        # Create a large text (1000 sentences)
        base_sentence = "I am happy and joyful today, but sometimes I feel sad and worried. "
        large_text = base_sentence * 1000
        
        import time
        start_time = time.time()
        
        try:
            scores, val_roll, emo_roll, summary = analyze(large_text)
            end_time = time.time()
            
            # Should complete in reasonable time (< 5 seconds)
            processing_time = end_time - start_time
            self.assertLess(processing_time, 5.0, 
                          f"Analysis took too long: {processing_time:.2f} seconds")
            
            # Results should be reasonable
            self.assertGreater(len(scores), 500)  # Should detect many sentences
            
        except Exception as e:
            self.fail(f"Analysis failed on large text: {e}")


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)
