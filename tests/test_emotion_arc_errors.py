#!/usr/bin/env python3
"""
Additional tests for error handling and edge cases in chapter_emotion_arc.py
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch

# Add tools directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from chapter_emotion_arc import main


class TestErrorHandling(unittest.TestCase):
    """Test error handling and input validation."""
    
    def test_invalid_window_size(self):
        """Test that invalid window sizes are rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content.")
            temp_file = f.name
        
        try:
            # Test negative window size
            test_args = ["chapter_emotion_arc.py", temp_file, "--window", "-1"]
            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(ValueError):
                    main()
            
            # Test zero window size
            test_args = ["chapter_emotion_arc.py", temp_file, "--window", "0"]
            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(ValueError):
                    main()
                    
        finally:
            os.unlink(temp_file)
    
    def test_directory_instead_of_file(self):
        """Test that directories are rejected as input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["chapter_emotion_arc.py", temp_dir]
            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(SystemExit):
                    main()
    
    def test_empty_file_handling(self):
        """Test handling of empty files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write only whitespace
            f.write("   \n\t  \n  ")
            temp_file = f.name
        
        try:
            test_args = ["chapter_emotion_arc.py", temp_file]
            with patch.object(sys, 'argv', test_args):
                # Should not crash, should handle gracefully
                try:
                    main()
                except SystemExit:
                    # SystemExit is acceptable for this case
                    pass
                    
        finally:
            os.unlink(temp_file)
    
    def test_output_file_error_handling(self):
        """Test error handling for output file issues."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("I am happy today.")
            temp_file = f.name
        
        try:
            # Try to write to an invalid directory
            invalid_csv = "/nonexistent/directory/output.csv"
            test_args = ["chapter_emotion_arc.py", temp_file, "--csv", invalid_csv]
            
            with patch.object(sys, 'argv', test_args):
                # Should handle the error gracefully and continue
                try:
                    main()
                except SystemExit:
                    # SystemExit is acceptable - the main execution should work
                    # even if file writing fails
                    pass
                    
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)
