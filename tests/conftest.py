"""
Test suite for the FFA Lab 9 writing analysis tools.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Test fixtures
@pytest.fixture
def sample_text():
    """Sample text for testing analysis tools."""
    return """
    John walked into the room with confidence. He was happy and excited about the meeting.
    "Hello everyone," he said cheerfully. "I'm glad to be here today."
    Mary responded with enthusiasm, "We're delighted to have you join us!"
    The atmosphere was joyful and full of trust. Everyone felt safe and comfortable.
    """

@pytest.fixture
def temp_text_file(sample_text):
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
