#!/usr/bin/env python3
"""
Script to automatically apply the latest editing plan to the story file using AI.
"""

import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
import subprocess
from pathlib import Path

def get_latest_editing_plan(output_dir):
    """
    Find the most recent editing plan file in the output directory.
    
    Args:
        output_dir (str): Path to the tests output directory
        
    Returns:
        str: Path to the latest editing plan file
    """
    editing_plans = []
    
    for filename in os.listdir(output_dir):
        if filename.startswith("EDITING_PLAN_") and filename.endswith(".md"):
            # Extract timestamp from filename
            timestamp_match = re.search(r'EDITING_PLAN_(\d{8}_\d{6})\.md', filename)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                editing_plans.append((timestamp, os.path.join(output_dir, filename)))
    
    if not editing_plans:
        raise ValueError("No editing plan files found in output directory")
    
    # Sort by timestamp and return the latest
    editing_plans.sort(key=lambda x: x[0], reverse=True)
    latest_plan = editing_plans[0][1]
    
    print(f"Found latest editing plan: {os.path.basename(latest_plan)}")
    return latest_plan

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

def save_file_content(file_path, content):
    """
    Save content to a file.
    
    Args:
        file_path (str): Path to the file
        content (str): Content to save
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def apply_edits_with_ai(story_content, editing_plan_content, model):
    """
    Use AI to apply the editing plan to the story content.
    
    Args:
        story_content (str): Original story content
        editing_plan_content (str): Editing plan content
        model (str): AI model to use
        
    Returns:
        str: Revised story content
    """
    
    # Construct the prompt for the AI
    prompt = f"""You are a professional editor tasked with applying specific edits to a story. 

Here is the ORIGINAL STORY:
```
{story_content}
```

Here is the DETAILED EDITING PLAN:
```
{editing_plan_content}
```

Your task is to:
1. Carefully read through the editing plan
2. Apply ONLY the specific edits mentioned in the plan
3. Make the changes exactly as recommended
4. Preserve everything else unchanged
5. Return ONLY the revised story content

IMPORTANT INSTRUCTIONS:
- Apply the edits precisely as specified in the editing plan
- Do NOT make any additional changes beyond what's in the plan
- If the plan says "NO CHANGE" for a section, leave it exactly as is
- Maintain the story's structure, formatting, and style
- Return the complete revised story, not just the changed parts

Please provide the fully edited story:"""

    # API payload
    api_payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1  # Low temperature for precise editing
    }
    
    # API call
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.getenv('open_router_key')
    if not api_key:
        raise ValueError("Missing OpenRouter API key. Set 'open_router_key' in your .env")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Sending editing request to AI...")
    response = requests.post(api_url, headers=headers, data=json.dumps(api_payload))
    response_json = response.json()
    
    # Extract the revised content
    revised_content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    if not revised_content:
        raise ValueError("Failed to get revised content from AI")
    
    return revised_content

def create_backup(file_path):
    """
    Create a backup of the original file with timestamp.
    
    Args:
        file_path (str): Path to the file to backup
        
    Returns:
        str: Path to the backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    # Copy the original file to backup
    import shutil
    shutil.copy2(file_path, backup_path)
    
    print(f"Created backup: {backup_path}")
    return backup_path

def git_commit_changes(file_path, editing_plan_path):
    """
    Commit the changes to git.
    
    Args:
        file_path (str): Path to the edited file
        editing_plan_path (str): Path to the editing plan used
    """
    # Honor ALLOW_GIT_COMMIT flag
    allow_commits = os.getenv('ALLOW_GIT_COMMIT', 'false').lower() in ('1', 'true', 'yes', 'on')
    if not allow_commits:
        print("(Skipping git commit: ALLOW_GIT_COMMIT is not enabled)")
        return
    try:
        project_root = os.getenv('project_root', '.')
        
        # Add the edited file to git
        subprocess.run(['git', 'add', file_path], cwd=project_root, check=True)
        
        # Create commit message with editing plan reference
        editing_plan_name = os.path.basename(editing_plan_path)
        commit_message = f"Auto-apply edits from {editing_plan_name}"
        
        # Commit the changes
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=project_root, check=True)
        
        print(f"✓ Git commit successful: {commit_message}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Git commit failed: {e}")
        raise

def main():
    """
    Main function to orchestrate the editing process.
    """
    # Load environment variables
    load_dotenv()
    
    # Get configuration from .env
    project_root = os.getenv('project_root', '.')
    tests_output_dir = os.getenv('tests_output_dir')
    test_source_dir = os.getenv('test_source_1')
    revision_model = os.getenv('text_model_5')  # AI model for revisions
    
    if not all([tests_output_dir, test_source_dir, revision_model]):
        raise ValueError("Missing required environment variables")
    
    # Convert to absolute paths if needed
    if tests_output_dir and not os.path.isabs(tests_output_dir):
        tests_output_dir = os.path.join(project_root, tests_output_dir)
    if test_source_dir and not os.path.isabs(test_source_dir):
        test_source_dir = os.path.join(project_root, test_source_dir)
    
    print(f"Using revision model: {revision_model}")
    print(f"Output directory: {tests_output_dir}")
    print(f"Source directory: {test_source_dir}")
    
    # Find the latest editing plan
    editing_plan_path = get_latest_editing_plan(tests_output_dir)
    editing_plan_content = read_file_content(editing_plan_path)
    
    # Find the story file to edit (assuming .md files in the source directory)
    if not test_source_dir:
        raise ValueError("test_source_dir is None")
        
    story_files = [f for f in os.listdir(test_source_dir) if f.endswith('.md')]
    if not story_files:
        raise ValueError(f"No .md files found in {test_source_dir}")
    
    # For now, edit the first .md file found
    story_file_path = os.path.join(test_source_dir, story_files[0])
    print(f"Editing story file: {story_files[0]}")
    
    # Read the original story content
    original_story_content = read_file_content(story_file_path)
    
    # Create a backup
    backup_path = create_backup(story_file_path)
    
    try:
        # Apply edits using AI
        print("Applying edits with AI...")
        revised_story_content = apply_edits_with_ai(
            original_story_content, 
            editing_plan_content, 
            revision_model
        )
        
        # Save the revised content
        save_file_content(story_file_path, revised_story_content)
        print(f"✓ Story file updated: {story_file_path}")
        
        # Show a preview of changes
        print("\n" + "="*50)
        print("PREVIEW OF REVISED STORY:")
        print("="*50)
        print(revised_story_content[:500] + ("..." if len(revised_story_content) > 500 else ""))
        print("="*50)
        
        # Commit to git (optional, guarded by ALLOW_GIT_COMMIT)
        git_commit_changes(story_file_path, editing_plan_path)
        
        print(f"\n✅ SUCCESS!")
        print(f"- Applied editing plan: {os.path.basename(editing_plan_path)}")
        print(f"- Updated story file: {story_files[0]}")
        print(f"- Created backup: {os.path.basename(backup_path)}")
        print(f"- Committed to git")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Restoring original file from backup...")
        
        # Restore from backup
        import shutil
        shutil.copy2(backup_path, story_file_path)
        print(f"✓ Original file restored")
        raise

if __name__ == "__main__":
    main()
