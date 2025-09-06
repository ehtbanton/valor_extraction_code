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

# --- 2. MAIN PROCESSING LOOP (The new, corrected, robust version) ---
print("\n--- Starting Main Processing Loop ---")
for target_idx, target in enumerate(pdd_targets):
    start_marker = target[1]
    end_marker = pdd_targets[target_idx + 1][1] if target_idx + 1 < len(pdd_targets) else "Appendix"

    # Status check remains the same as your original
    current_output_text = load_word_doc_to_string("auto_pdd_output")
    start_loc_output = find_target_location(target, current_output_text)
    end_loc_output = find_target_location(pdd_targets[target_idx + 1], current_output_text) if target_idx + 1 < len(pdd_targets) else -1
    section_content_from_output = current_output_text[start_loc_output:end_loc_output] if end_loc_output != -1 else current_output_text[start_loc_output:]
    
    if("SECTION_COMPLETE" in section_content_from_output):
        print(f"\nSection '{start_marker}' is already complete. Skipping...")
        continue
    if("SECTION_ATTEMPTED" in section_content_from_output):
        if(not there_are_new_files):
            print(f"\nSection '{start_marker}' attempted; no new files. Skipping...")
            continue
        print(f"\nSection '{start_marker}' attempted, new files available. Retrying...")
    
    print(f"\n{'='*20}\nProcessing section: {start_marker}\n{'='*20}")
    
    # Get the placeholder section text from the clean template to send to the AI
    start_loc_template = find_target_location(target, template_text)
    end_loc_template = find_target_location(pdd_targets[target_idx + 1], template_text) if target_idx + 1 < len(pdd_targets) else -1
    infilling_info = template_text[start_loc_template:end_loc_template] if end_loc_template != -1 else template_text[start_loc_template:]

    system_prompt = assemble_system_prompt()
    user_prompt = assemble_user_prompt(infilling_info)

    # --- THIS IS THE NEW, SIMPLIFIED API CALL AND PROCESSING LOGIC ---
    print("  > Gemini API Call...")
    response_str = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
    
    print("\n--- AI JSON Response ---")
    print(response_str)
    print("-----------------------\n")

    if "An error occurred while asking Gemini" in response_str:
        print(f"  > !!! API ERROR: {response_str}. Skipping section.")
        continue

    # Attempt to parse the AI's response into a dictionary using our new helper
    ai_json_data = parse_ai_json_response(response_str)

    if ai_json_data is None:
        print(f"  > Skipping update for section '{start_marker}' due to invalid JSON from AI.")
        continue

    # Determine status by checking the values in the successfully parsed JSON
    is_complete = not any(data.get("value") == "INFO_NOT_FOUND" for data in ai_json_data.values())
    status = "SECTION_COMPLETE" if is_complete else "SECTION_ATTEMPTED"
    
    # Call the robust word editor with the correct arguments
    replace_section_in_word_doc(output_path, start_marker, end_marker, ai_json_data, status)
    # --- END OF THE NEW LOGIC ---

    user_input = input("\nPress Enter to continue, or 'q' to quit: ")
    if user_input.lower() == 'q':
        break

print(f"\nProcessing complete. The final document has been saved at: {output_path}")