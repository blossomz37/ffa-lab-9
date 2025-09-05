#!/usr/bin/env python3
"""
Script to automatically generate HTML comparison documents for story revisions.
Finds the most recent backup and current story file, then creates a visual diff.
"""

import os
import re
import glob
from datetime import datetime
from dotenv import load_dotenv
import difflib
from pathlib import Path

def find_latest_backup(source_dir, story_filename):
    """
    Find the most recent backup file for a given story.
    
    Args:
        source_dir (str): Directory containing the story files
        story_filename (str): Base filename of the story
        
    Returns:
        str: Path to the most recent backup file, or None if not found
    """
    # Look for backup files with timestamp pattern
    backup_pattern = f"{story_filename}.backup_*"
    backup_files = glob.glob(os.path.join(source_dir, backup_pattern))
    
    if not backup_files:
        return None
    
    # Sort by timestamp (assuming format: filename.backup_YYYYMMDD_HHMMSS)
    backup_files.sort(key=lambda x: os.path.basename(x).split('_')[-2:], reverse=True)
    
    return backup_files[0]

def find_latest_editing_plan(output_dir):
    """
    Find the most recent editing plan file.
    
    Args:
        output_dir (str): Directory containing editing plan files
        
    Returns:
        str: Filename of the latest editing plan
    """
    editing_plans = []
    
    for filename in os.listdir(output_dir):
        if filename.startswith("EDITING_PLAN_") and filename.endswith(".md"):
            timestamp_match = re.search(r'EDITING_PLAN_(\d{8}_\d{6})\.md', filename)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                editing_plans.append((timestamp, filename))
    
    if not editing_plans:
        return "Unknown editing plan"
    
    # Sort by timestamp and return the latest
    editing_plans.sort(key=lambda x: x[0], reverse=True)
    return editing_plans[0][1]

def read_file_content(file_path):
    """
    Read content from a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File content
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_title_from_content(content):
    """
    Extract title from markdown content.
    
    Args:
        content (str): File content
        
    Returns:
        str: Extracted title or default
    """
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Unknown Story"

def create_word_level_diff(original_text, revised_text):
    """
    Create a word-level diff highlighting changes.
    
    Args:
        original_text (str): Original text
        revised_text (str): Revised text
        
    Returns:
        tuple: (original_with_markup, revised_with_markup, stats)
    """
    # Split into words while preserving structure
    original_words = re.split(r'(\s+)', original_text)
    revised_words = re.split(r'(\s+)', revised_text)
    
    # Create diff
    diff = list(difflib.unified_diff(
        original_words, revised_words,
        lineterm='', n=0
    ))
    
    # Process diff to create markup
    original_markup = []
    revised_markup = []
    changes_count = 0
    words_added = 0
    words_removed = 0
    
    # Use SequenceMatcher for better word-level comparison
    matcher = difflib.SequenceMatcher(None, original_words, revised_words)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Unchanged text
            text_chunk = ''.join(original_words[i1:i2])
            original_markup.append(text_chunk)
            revised_markup.append(text_chunk)
        elif tag == 'delete':
            # Deleted text (only in original)
            deleted_text = ''.join(original_words[i1:i2])
            original_markup.append(f'<span class="deletion">{deleted_text}</span>')
            words_removed += len([w for w in original_words[i1:i2] if w.strip()])
            changes_count += 1
        elif tag == 'insert':
            # Inserted text (only in revised)
            inserted_text = ''.join(revised_words[j1:j2])
            revised_markup.append(f'<span class="insertion">{inserted_text}</span>')
            words_added += len([w for w in revised_words[j1:j2] if w.strip()])
            changes_count += 1
        elif tag == 'replace':
            # Replaced text
            deleted_text = ''.join(original_words[i1:i2])
            inserted_text = ''.join(revised_words[j1:j2])
            original_markup.append(f'<span class="deletion">{deleted_text}</span>')
            revised_markup.append(f'<span class="insertion">{inserted_text}</span>')
            words_removed += len([w for w in original_words[i1:i2] if w.strip()])
            words_added += len([w for w in revised_words[j1:j2] if w.strip()])
            changes_count += 1
    
    stats = {
        'total_changes': changes_count,
        'words_added': words_added,
        'words_removed': words_removed,
        'net_change': words_added - words_removed
    }
    
    return ''.join(original_markup), ''.join(revised_markup), stats

def format_content_for_html(content, line_numbers=True):
    """
    Format content for HTML display with proper paragraph breaks.
    
    Args:
        content (str): Raw content with markup
        line_numbers (bool): Whether to add line numbers
        
    Returns:
        str: HTML formatted content
    """
    lines = content.split('\n')
    html_lines = []
    line_num = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('# '):
            # Header
            html_lines.append(f'<h1>{line}</h1>')
        elif line:
            # Regular paragraph with optional line numbers
            if line_numbers:
                line_prefix = f'<span class="line-numbers">{line_num}</span>'
                html_lines.append(f'<p>{line_prefix}{line}</p>')
                line_num += 1
            else:
                html_lines.append(f'<p>{line}</p>')
    
    return '\n'.join(html_lines)

def generate_comparison_html(original_file, revised_file, template_file, output_file, editing_plan_name):
    """
    Generate HTML comparison document using template.
    
    Args:
        original_file (str): Path to original file
        revised_file (str): Path to revised file
        template_file (str): Path to HTML template
        output_file (str): Path for output HTML
        editing_plan_name (str): Name of editing plan used
    """
    # Read file contents
    original_content = read_file_content(original_file)
    revised_content = read_file_content(revised_file)
    template_content = read_file_content(template_file)
    
    # Extract title
    title = extract_title_from_content(revised_content)
    
    # Create word-level diff
    original_markup, revised_markup, stats = create_word_level_diff(original_content, revised_content)
    
    # Format for HTML
    original_html = format_content_for_html(original_markup, line_numbers=True)
    revised_html = format_content_for_html(revised_markup, line_numbers=True)
    
    # Replace template placeholders
    html_content = template_content.replace('{{TITLE}}', title)
    html_content = html_content.replace('{{GENERATION_DATE}}', datetime.now().strftime('%B %d, %Y at %I:%M %p'))
    html_content = html_content.replace('{{EDITING_PLAN}}', editing_plan_name)
    html_content = html_content.replace('{{ORIGINAL_CONTENT}}', original_html)
    html_content = html_content.replace('{{REVISED_CONTENT}}', revised_html)
    
    # Replace stats placeholders
    html_content = html_content.replace('{{TOTAL_CHANGES}}', str(stats['total_changes']))
    html_content = html_content.replace('{{WORDS_ADDED}}', str(stats['words_added']))
    html_content = html_content.replace('{{WORDS_REMOVED}}', str(stats['words_removed']))
    
    net_change = stats['net_change']
    net_change_str = f"+{net_change}" if net_change > 0 else str(net_change)
    html_content = html_content.replace('{{NET_CHANGE}}', net_change_str)
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    """
    Main function to orchestrate the comparison generation.
    """
    # Load environment variables
    load_dotenv()
    
    # Get configuration from .env
    project_root = os.getenv('project_root', '.')
    tests_output_dir = os.getenv('tests_output_dir')
    test_source_dir = os.getenv('test_source_1')
    
    if not all([tests_output_dir, test_source_dir]):
        raise ValueError("Missing required environment variables")
    
    # Convert to absolute paths if needed
    if tests_output_dir and not os.path.isabs(tests_output_dir):
        tests_output_dir = os.path.join(project_root, tests_output_dir)
    if test_source_dir and not os.path.isabs(test_source_dir):
        test_source_dir = os.path.join(project_root, test_source_dir)
    
    print(f"Source directory: {test_source_dir}")
    print(f"Output directory: {tests_output_dir}")
    
    # Find story files
    if not test_source_dir:
        raise ValueError("test_source_dir is None")
        
    story_files = [f for f in os.listdir(test_source_dir) if f.endswith('.md') and not f.endswith('.backup')]
    if not story_files:
        raise ValueError(f"No .md files found in {test_source_dir}")
    
    # Process each story file
    for story_file in story_files:
        print(f"\nProcessing: {story_file}")
        
        story_path = os.path.join(test_source_dir, story_file)
        backup_path = find_latest_backup(test_source_dir, story_file)
        
        if not backup_path:
            print(f"  ⚠️  No backup found for {story_file}, skipping...")
            continue
        
        print(f"  📄 Original: {os.path.basename(backup_path)}")
        print(f"  ✏️  Revised: {story_file}")
        
        # Find latest editing plan
        editing_plan_name = find_latest_editing_plan(tests_output_dir)
        print(f"  📋 Editing plan: {editing_plan_name}")
        
        # Set up paths
        template_path = os.path.join(project_root, 'templates', 'story_comparison_template.html')
        output_dir = os.path.join(project_root, 'output', 'html')
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        base_name = os.path.splitext(story_file)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_name}_comparison_{timestamp}.html"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Generate comparison
            generate_comparison_html(
                backup_path, story_path, template_path, 
                output_path, editing_plan_name
            )
            
            print(f"  ✅ Generated: {output_filename}")
            print(f"     📍 Location: {output_path}")
            
        except Exception as e:
            print(f"  ❌ Error generating comparison: {e}")
    
    print(f"\n🎉 Comparison generation complete!")

if __name__ == "__main__":
    main()
