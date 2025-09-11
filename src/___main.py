import os
import json
from gemini_interface import setup_gemini, ask_gemini, upload_files_to_gemini
from context_manager import extract_text_from_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location, assemble_system_prompt, assemble_user_prompt, parse_ai_json_response
from word_editor import load_word_doc_to_string, create_output_doc_from_template, replace_section_in_word_doc

os.system('cls' if os.name == 'nt' else 'clear')

# --- 1. SETUP (Your original, working setup code) ---
project_name = "prime_road"

output_path = create_output_doc_from_template(project_name)

template_text = load_word_doc_to_string("output_template")
if "Error:" in template_text:
    print(f"FATAL ERROR reading template: {template_text}")
    exit()

contents_list = retrieve_contents_list(template_text)
pdd_targets = get_pdd_targets(contents_list)

if not pdd_targets:
    print("FATAL ERROR: Could not find a valid 'Contents' section in the document from 'output_template'.")
    print("The main processing loop has no sections to process. Exiting.")
    exit()

there_are_new_files = extract_text_from_folder(f"provided_documents/{project_name}")
GEMINI_CLIENT = setup_gemini()
uploaded_files_cache = upload_files_to_gemini([f"provided_documents/{project_name}/all_context.txt"])

# --- 2. MAIN PROCESSING LOOP (Enhanced with better debugging) ---
print("\n--- Starting Main Processing Loop ---")
for target_idx, target in enumerate(pdd_targets):
    # Use the subheading_idx + subheading format (e.g., "1.1 Summary Description of the Project")
    start_marker = f"{target[2]} {target[1]}"
    next_target = pdd_targets[target_idx + 1] if target_idx + 1 < len(pdd_targets) else None
    end_marker = f"{next_target[2]} {next_target[1]}" if next_target else "Appendix"

    # Status check with proper section marker format
    current_output_text = load_word_doc_to_string("auto_pdd_output")
    
    # Create target tuples for find_target_location
    current_target_tuple = (target[0], start_marker, target[2], target[3])
    next_target_tuple = (next_target[0], end_marker, next_target[2], next_target[3]) if next_target else None
    
    start_loc_output = find_target_location(current_target_tuple, current_output_text)
    end_loc_output = find_target_location(next_target_tuple, current_output_text) if next_target_tuple else -1
    section_content_from_output = current_output_text[start_loc_output:end_loc_output] if end_loc_output != -1 else current_output_text[start_loc_output:]
    
    if("SECTION_COMPLETE" in section_content_from_output):
        print(f"\nSection '{start_marker}' is already complete. Skipping...")
        continue
    if("SECTION_ATTEMPTED" in section_content_from_output):
        if(not there_are_new_files):
            print(f"\nSection '{start_marker}' attempted; no new files. Skipping...")
            continue
        print(f"\nSection '{start_marker}' attempted, new files available. Retrying...")
    
    print(f"\n{'='*60}\nProcessing section: {start_marker}\n{'='*60}")
    
    # Get the placeholder section text from the clean template to send to the AI
    start_loc_template = find_target_location(current_target_tuple, template_text)
    end_loc_template = find_target_location(next_target_tuple, template_text) if next_target_tuple else -1
    infilling_info = template_text[start_loc_template:end_loc_template] if end_loc_template != -1 else template_text[start_loc_template:]

    # Show a preview of what we're processing
    print("\n--- Template Section Preview (first 500 chars) ---")
    print(infilling_info[:500] + "..." if len(infilling_info) > 500 else infilling_info)
    print("-" * 50)

    system_prompt = assemble_system_prompt()
    user_prompt = assemble_user_prompt(infilling_info)

    # API Call
    print("\n  > Calling Gemini API...")
    response_str = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
    
    print("\n--- AI JSON Response (first 1000 chars) ---")
    print(response_str[:1000] + "..." if len(response_str) > 1000 else response_str)
    print("-" * 50)

    if "An error occurred while asking Gemini" in response_str:
        print(f"  > !!! API ERROR: {response_str}. Skipping section.")
        continue

    # Attempt to parse the AI's response
    ai_json_data = parse_ai_json_response(response_str)

    if ai_json_data is None:
        print(f"  > Skipping update for section '{start_marker}' due to invalid JSON from AI.")
        continue

    # Show what keys the AI returned
    print(f"\n  > AI returned {len(ai_json_data)} data fields:")
    for i, key in enumerate(list(ai_json_data.keys())[:5]):  # Show first 5 keys
        value_obj = ai_json_data[key]
        if isinstance(value_obj, dict):
            value = value_obj.get("value", "")
            if value and value != "INFO_NOT_FOUND":
                preview = value[:50] + "..." if len(value) > 50 else value
                print(f"    {i+1}. {key}: {preview}")
    if len(ai_json_data) > 5:
        print(f"    ... and {len(ai_json_data) - 5} more fields")

    # Determine status
    is_complete = not any(
        isinstance(data, dict) and data.get("value") == "INFO_NOT_FOUND" 
        for data in ai_json_data.values()
    )
    status = "SECTION_COMPLETE" if is_complete else "SECTION_ATTEMPTED"
    
    # Call the word editor with the parsed data
    replace_section_in_word_doc(output_path, start_marker, end_marker, ai_json_data, status)

    user_input = input("\nPress Enter to continue, or 'q' to quit: ")
    if user_input.lower() == 'q':
        break

print(f"\nProcessing complete. The final document has been saved at: {output_path}")