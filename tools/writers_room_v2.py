import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

def prepare_file_for_api(file_path, file_type):
    """
    Prepare a file for API transmission by reading its content and metadata.

    Args:
        file_path (str): The path to the file.
        file_type (str): The type of the file (e.g., 'text').

    Returns:
        dict: A dictionary containing the file's metadata and content.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    return {
        "type": file_type,
        "content": content,
        "name": file_name,
        "size": file_size
    }

def save_to_file(content, file_path):
    """
    Save content to a file.

    Args:
        content (str): The content to save.
        file_path (str): The path to the file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def generate_unique_filename(base_name, extension):
    """
    Generate a unique filename by appending a timestamp.

    Args:
        base_name (str): The base name of the file.
        extension (str): The file extension.

    Returns:
        str: A unique filename with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

def update_conversation_history(history, assistant_response, persona=None):
    """
    Update the conversation history with just the assistant's response.

    Args:
        history (list): The current conversation history.
        assistant_response (str): The assistant's response.
        persona (str): The persona used for the assistant's response (optional).

    Returns:
        list: The updated conversation history.
    """
    from datetime import datetime

    # Create the history entry for the assistant response
    assistant_entry = {"timestamp": datetime.now().isoformat(), "role": "assistant", "content": assistant_response}
    if persona:
        assistant_entry["persona"] = persona

    # Append the new entry
    history.append(assistant_entry)

    return history

def save_history_to_file(history, history_file):
    """
    Save the conversation history to a file.

    Args:
        history (list): The conversation history to save.
        history_file (str): Path to the conversation history file.
    """
    with open(history_file, 'w', encoding='utf-8') as file:
        json.dump(history, file, indent=4)

def get_persona_details(persona_id):
    """
    Retrieve the persona details from the .env file.

    Args:
        persona_id (int): The persona number (e.g., 1, 2, 3, etc.).

    Returns:
        dict: A dictionary containing the persona's model and file path.
    """
    persona_key = f"writers_room_persona_{persona_id}"
    model_key = f"text_model_{persona_id}"

    persona_file = os.getenv(persona_key)
    model = os.getenv(model_key)

    if not persona_file or not model:
        raise ValueError(f"Missing details for persona {persona_id}. Check your .env file.")

    # Handle both absolute and relative paths
    if not os.path.isabs(persona_file):
        project_root = os.getenv('project_root', '.')
        persona_file = os.path.join(project_root, persona_file)

    return {"file": persona_file, "model": model}

def prepare_persona_payload(persona_id, history, round_number=1):
    """
    Prepare the API payload for a specific persona.

    Args:
        persona_id (int): The persona number.
        history (list): The conversation history.
        round_number (int): Which round of conversation (1, 2, or 3).

    Returns:
        dict: The API payload for the persona.
    """
    persona_details = get_persona_details(persona_id)

    # Read the persona file content
    with open(persona_details["file"], 'r', encoding='utf-8') as file:
        persona_content = file.read()

    # Different instructions for each round
    if round_number == 1:
        instruction = "Play the attached role and provide your initial analysis of the story."
    elif round_number == 2:
        instruction = "Now that you've heard from the other personas, address them directly. You can agree, disagree, question their points, or build on their ideas. Make sure to engage with the conversation."
    elif round_number == 3:
        instruction = "This is the consensus round. Consider what the other personas have said and work toward agreement on the key issues and priorities for revising this story. Focus on finding common ground and identifying the most important changes needed."
    else:
        instruction = "Play the attached role and provide your analysis."

    # Construct the user message
    user_message = (
        f"{instruction} Here is your persona description:\n\n"
        f"[start persona]\n{persona_content}\n[end persona]\n\n"
        "Here is the conversation history for context:\n\n"
        f"[start history]\n{json.dumps(history, indent=4)}\n[end history]"
    )

    # API payload
    return {
        "model": persona_details["model"],
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get paths from environment variables with smart path handling
    project_root = os.getenv('project_root', '.')
    tests_output_dir = os.getenv('tests_output_dir', 'tests/tests_output')
    api_key = os.getenv('open_router_key')
    if not api_key:
        raise ValueError("Missing OpenRouter API key. Set 'open_router_key' in your .env")
    
    # Handle absolute vs relative paths
    if os.path.isabs(tests_output_dir):
        output_dir = tests_output_dir
    else:
        output_dir = os.path.join(project_root, tests_output_dir)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Path to the conversation history file with unique filename
    unique_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_filename = f"conversation_history_{unique_timestamp}.json"
    history_file = os.path.join(output_dir, history_filename)
    
    print(f"Using conversation history file: {history_filename}")

    # Initialize conversation history
    print("Initializing conversation history with story content.")
    # Get the source directory from .env
    source_dir_config = os.getenv('test_source_1')
    if not source_dir_config:
        raise ValueError("test_source_1 not found in .env file")
    
    # Handle absolute vs relative paths
    if os.path.isabs(source_dir_config):
        source_dir = source_dir_config
    else:
        source_dir = os.path.join(project_root, source_dir_config)
    
    # Read all text files from the source directory
    story_content = ""
    for filename in os.listdir(source_dir):
        if filename.endswith(('.md', '.txt')):
            file_path = os.path.join(source_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                story_content += f"=== {filename} ===\n{file.read()}\n\n"
    
    if not story_content:
        raise ValueError(f"No .md or .txt files found in {source_dir}")
        
    history = [
        {
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": story_content
        }
    ]
    save_history_to_file(history, history_file)

    # Run three rounds of conversation
    for round_number in range(1, 4):
        print(f"\n=== ROUND {round_number} ===")
        if round_number == 1:
            print("Initial Analysis Round")
        elif round_number == 2:
            print("Discussion Round - Personas Address Each Other")
        else:
            print("Consensus Round - Working Toward Agreement")
        
        # Iterate over personas 1 to 4 for this round
        for persona_id in range(1, 5):
            try:
                print(f"Processing Persona {persona_id} (Round {round_number})...")

                # Prepare the payload for the persona with round-specific instructions
                api_payload = prepare_persona_payload(persona_id, history, round_number)

                # Generate unique filenames with round number
                raw_request_filename = generate_unique_filename(f"persona_{persona_id}_round_{round_number}_api_request", "json")
                raw_response_filename = generate_unique_filename(f"persona_{persona_id}_round_{round_number}_api_response", "json")
                markdown_filename = generate_unique_filename(f"persona_{persona_id}_round_{round_number}_interaction_summary", "md")

                raw_request_path = os.path.join(output_dir, raw_request_filename)
                raw_response_path = os.path.join(output_dir, raw_response_filename)
                markdown_path = os.path.join(output_dir, markdown_filename)

                # Save raw JSON request
                save_to_file(json.dumps(api_payload, indent=4), raw_request_path)

                # API endpoint and headers
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # Send the payload via API
                response = requests.post(api_url, headers=headers, data=json.dumps(api_payload))
                response_json = response.json()

                # Extract the assistant's response
                assistant_response = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")

                print(f"Response for Persona {persona_id} (Round {round_number}): {assistant_response[:100]}...")

                # Save raw JSON response
                save_to_file(json.dumps(response_json, indent=4), raw_response_path)

                # Generate markdown version
                markdown_content = """# Persona {persona_id} Round {round_number} Interaction Summary

## User Message
{user_message}

## Assistant Response
{assistant_response}
""".format(
                    persona_id=persona_id,
                    round_number=round_number,
                    user_message=api_payload["messages"][0]["content"],
                    assistant_response=assistant_response
                )

                save_to_file(markdown_content, markdown_path)

                # Update the conversation history with just the assistant's response
                history = update_conversation_history(
                    history,
                    assistant_response,
                    persona=f"Persona {persona_id}"
                )
                save_history_to_file(history, history_file)

                print(f"Persona {persona_id} Round {round_number} files saved:")
                print(f"- Raw request: {raw_request_path}")
                print(f"- Raw response: {raw_response_path}")
                print(f"- Markdown summary: {markdown_path}")

            except Exception as e:
                print(f"An error occurred for Persona {persona_id} Round {round_number}: {e}")
    
    # Final step: Phoenix creates the editing plan
    print(f"\n=== FINAL EDITING PLAN ===")
    print("Phoenix creating detailed editing plan...")
    
    try:
        # Special instruction for Phoenix to create the editing plan
        editing_instruction = (
            "Based on the entire conversation above, create a very specific editing plan for the original story. "
            "For each recommended change, provide:\n"
            "1. The exact passage that needs revision (quote it exactly)\n"
            "2. The specific recommended edit\n"
            "3. The reason for the change\n\n"
            "Be very detailed and actionable so the author knows exactly what to change and how."
        )
        
        phoenix_details = get_persona_details(3)  # Phoenix is persona 3
        with open(phoenix_details["file"], 'r', encoding='utf-8') as file:
            phoenix_content = file.read()

        editing_payload = {
            "model": phoenix_details["model"],
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"{editing_instruction}\n\n"
                        f"Here is your persona description:\n\n"
                        f"[start persona]\n{phoenix_content}\n[end persona]\n\n"
                        "Here is the complete conversation history:\n\n"
                        f"[start history]\n{json.dumps(history, indent=4)}\n[end history]"
                    )
                }
            ]
        }

        # Generate filenames for editing plan
        editing_request_filename = generate_unique_filename("phoenix_editing_plan_request", "json")
        editing_response_filename = generate_unique_filename("phoenix_editing_plan_response", "json")
        editing_plan_filename = generate_unique_filename("EDITING_PLAN", "md")

        editing_request_path = os.path.join(output_dir, editing_request_filename)
        editing_response_path = os.path.join(output_dir, editing_response_filename)
        editing_plan_path = os.path.join(output_dir, editing_plan_filename)

        # Save raw JSON request
        save_to_file(json.dumps(editing_payload, indent=4), editing_request_path)

        # API endpoint and headers
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Send the payload via API
        response = requests.post(api_url, headers=headers, data=json.dumps(editing_payload))
        response_json = response.json()

        # Extract the editing plan
        editing_plan = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No editing plan generated")

        print(f"Editing plan generated: {editing_plan[:150]}...")

        # Save raw JSON response
        save_to_file(json.dumps(response_json, indent=4), editing_response_path)

        # Save the editing plan as markdown
        save_to_file(editing_plan, editing_plan_path)

        # Add the editing plan to conversation history
        history = update_conversation_history(
            history,
            editing_plan,
            persona="Phoenix (Editing Plan)"
        )
        save_history_to_file(history, history_file)

        print(f"EDITING PLAN files saved:")
        print(f"- Raw request: {editing_request_path}")
        print(f"- Raw response: {editing_response_path}")
        print(f"- EDITING PLAN: {editing_plan_path}")

        # Git commit the important files (guarded by ALLOW_GIT_COMMIT)
        print(f"\n=== GIT COMMITS ===")
        try:
            allow_commits = os.getenv('ALLOW_GIT_COMMIT', 'false').lower() in ('1', 'true', 'yes', 'on')
            if not allow_commits:
                print("(Skipping git commits: ALLOW_GIT_COMMIT is not enabled)")
            else:
                # Get paths from environment variables
                project_root = os.getenv('project_root', '.')
                source_dir_relative = os.getenv('test_source_1')
                if source_dir_relative:
                    source_dir = os.path.join(project_root, source_dir_relative)
                else:
                    source_dir = "tests/tests_input"  # fallback
                
                # Commit source files
                run_git_command(f"git add {source_dir}/*", "Adding source files to git")
                run_git_command(f'git commit -m "Add source files for writers room session {unique_timestamp}"', "Committing source files")
                
                # Commit conversation history
                run_git_command(f"git add {history_file}", "Adding conversation history to git")
                run_git_command(f'git commit -m "Add conversation history {history_filename}"', "Committing conversation history")
                
                # Commit editing plan
                run_git_command(f"git add {editing_plan_path}", "Adding editing plan to git")
                run_git_command(f'git commit -m "Add editing plan from writers room session {unique_timestamp}"', "Committing editing plan")
                
                print("Git commits completed successfully!")
            
        except Exception as git_error:
            print(f"Git commit error (non-critical): {git_error}")

    except Exception as e:
        print(f"An error occurred creating the editing plan: {e}")

def run_git_command(command, description):
    """Helper function to run git commands (guarded by ALLOW_GIT_COMMIT)"""
    import subprocess
    try:
        allow_commits = os.getenv('ALLOW_GIT_COMMIT', 'false').lower() in ('1', 'true', 'yes', 'on')
        if not allow_commits:
            print(f"(Skipping: {description}. ALLOW_GIT_COMMIT is not enabled)")
            return None
        project_root = os.getenv('project_root', '.')
        result = subprocess.run(command, shell=True, cwd=project_root, 
                              capture_output=True, text=True, check=True)
        print(f"✓ {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}: {e.stderr}")
        return None

if __name__ == "__main__":
    main()
