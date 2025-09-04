#!/usr/bin/env python3
"""
Setup script for FFA Lab 9 - MCP Writing Tools
Educational project for building AI-assisted writing tools
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ffa-lab-9",
    version="1.0.0",
    description="Educational MCP tools for AI-assisted writing and authoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FFA Lab 9 Contributors",
    author_email="carlo@example.com",
    url="https://github.com/blossomz37/ffa-lab-9",
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=[
        "tools.chapter_emotion_arc",
        "tools.chapter_beats_detection", 
        "tools.chapter_character_dialogue",
        "tools.chapter_continuity_consistency",
        "tools.chapter_lexical_diversity",
        "tools.chapter_mechanics_cleanup",
        "tools.chapter_structural_analysis", 
        "tools.chapter_style_readability",
        "tools.writers_room_v2",
        "tools.apply_editing_plan",
        "tools.generate_html_comparison",
        "tools.memory_mcp"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="education mcp ai writing tools analysis nlp",
    python_requires=">=3.8",
    install_requires=[
        # Core functionality uses only built-in libraries
        # Optional dependencies listed in requirements.txt
    ],
    extras_require={
        "viz": ["matplotlib>=3.5.0", "plotly>=5.0.0"],
        "data": ["pandas>=1.3.0", "numpy>=1.21.0"], 
        "web": ["fastapi>=0.68.0", "uvicorn>=0.15.0"],
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ffa-emotion-arc=tools.chapter_emotion_arc:main",
            "ffa-beats=tools.chapter_beats_detection:main",
            "ffa-dialogue=tools.chapter_character_dialogue:main",
            "ffa-writers-room=tools.writers_room_v2:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["samples/*.txt", "README.md", "LICENSE"],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/blossomz37/ffa-lab-9/issues",
        "Source": "https://github.com/blossomz37/ffa-lab-9",
        "Documentation": "https://github.com/blossomz37/ffa-lab-9#readme",
    },
)
