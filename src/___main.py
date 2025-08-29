import os
import json
from gemini_interface import setup_gemini, ask_gemini, upload_files_to_gemini
from context_manager import extract_text_from_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location, assemble_system_prompt, assemble_user_prompt, is_valid_response
from word_editor import load_word_doc_to_string, create_output_doc_from_template, replace_section_in_word_doc

os.system('cls' if os.name == 'nt' else 'clear')

# --- 1. SETUP ---
project_name = "prime_road"

# Creates the output file at the start. This is correct.
output_path = create_output_doc_from_template(project_name)

# *** THE CRITICAL FIX IS HERE ***
# We MUST load the structure (the "Contents" list) from the original, clean template.
# This ensures the pdd_targets list is always created correctly.
template_text = load_word_doc_to_string("output_template")
if "Error:" in template_text:
    print(f"FATAL ERROR reading template: {template_text}")
    exit()

contents_list = retrieve_contents_list(template_text)
pdd_targets = get_pdd_targets(contents_list)

# Add a check to ensure the program has tasks to perform
if not pdd_targets:
    print("FATAL ERROR: Could not find a valid 'Contents' section in the document from 'output_template'.")
    print("The main processing loop has no sections to process. Exiting.")
    exit()

there_are_new_files = extract_text_from_folder(f"provided_documents/{project_name}")
GEMINI_CLIENT = setup_gemini()
uploaded_files_cache = upload_files_to_gemini([f"provided_documents/{project_name}/all_context.txt"])

# --- 2. MAIN PROCESSING LOOP ---
print("\n--- Starting Main Processing Loop ---")
for target_idx, target in enumerate(pdd_targets):
    # 'target' is a tuple: (section_heading, subheading, subheading_idx, page_num)
    start_marker = target[1]  # The subheading title is our start marker

    if target_idx + 1 < len(pdd_targets):
        end_marker = pdd_targets[target_idx + 1][1]
    else:
        end_marker = "Appendix"

    # To check the status, we read the CURRENT state of the output document
    current_output_text = load_word_doc_to_string("auto_pdd_output")
    start_loc_output = find_target_location(target, current_output_text)
    end_loc_output = find_target_location(pdd_targets[target_idx + 1], current_output_text) if target_idx + 1 < len(pdd_targets) else -1
    section_content_from_output = current_output_text[start_loc_output:end_loc_output] if end_loc_output != -1 else current_output_text[start_loc_output:]
    
    # Get the ORIGINAL placeholder text from the clean template to send to the AI
    start_loc_template = find_target_location(target, template_text)
    end_loc_template = find_target_location(pdd_targets[target_idx + 1], template_text) if target_idx + 1 < len(pdd_targets) else -1
    infilling_info = template_text[start_loc_template:end_loc_template] if end_loc_template != -1 else template_text[start_loc_template:]

    if("SECTION_COMPLETE" in section_content_from_output):
        print(f"\nSection '{start_marker}' is already complete. Skipping...")
        continue
    if("SECTION_ATTEMPTED" in section_content_from_output):
        if(not there_are_new_files):
            print(f"\nSection '{start_marker}' has previously been attempted and no new files are available. Skipping...")
            continue
        print(f"\nSection '{start_marker}' has previously been attempted, but there are new files! Retrying...")
        # Future refill logic will go here
    
    print(f"\n{'='*20}\nProcessing section: {start_marker}\n{'='*20}")
    
    system_prompt = assemble_system_prompt()
    user_prompt = assemble_user_prompt(infilling_info)
    response = ""
    for i in range(3):
        print(f"  > Gemini API Call (Attempt {i+1})...")
        response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
        if is_valid_response(response, infilling_info):
            print("  > Valid response received from Gemini.")
            break
        elif i < 2:
            print("  > Invalid response format, retrying...")
        else:
            print("  > Failed to get a valid response after 3 attempts.")
            # Decide if you want to exit or continue
            continue # Continue to next section

    print("\n--- Response ---")
    print(response)
    print("-----------------------\n")

    if("INFO_NOT_FOUND" not in response):
        response = "SECTION_COMPLETE\n\n"+response
        print("SECTION_COMPLETE")
    else:
        response = "SECTION_ATTEMPTED\n\n"+response
        print("SECTION_ATTEMPTED")

    # This call now works because the loop is running and `word_editor` is robust
    replace_section_in_word_doc(output_path, start_marker, end_marker, response)

    user_input = input("\nPress Enter to continue to the next section, or 'q' to quit: ")
    if user_input.lower() == 'q':
        break

print(f"\nProcessing complete. The final document has been saved at: {output_path}")