import os
from gemini_interface import setup_gemini, ask_gemini, upload_files_to_gemini
from file_manager import extract_text_from_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location, assemble_system_prompt, assemble_user_prompt, is_valid_response
from template_text_loader import load_word_doc_to_string
# Import the new, capable word editor functions
from word_editor import create_output_doc_from_template, replace_section_in_word_doc

os.system('cls' if os.name == 'nt' else 'clear')

# --- 1. SETUP ---
project_name = "prime_road"

# Create the single output document from the template at the very beginning.
# This solves the problem of creating a new file on each run.
output_path = create_output_doc_from_template(project_name)

# Load the template's structure into a string for analysis and for generating prompts
template_text = load_word_doc_to_string("output_template")
contents_list = retrieve_contents_list(template_text)
pdd_targets = get_pdd_targets(contents_list)

# Prepare context documents for Gemini
extract_text_from_folder(f"provided_documents/{project_name}")
GEMINI_CLIENT = setup_gemini()
uploaded_files_cache = upload_files_to_gemini([f"provided_documents/{project_name}/provided_docs.txt"])

# --- 2. MAIN PROCESSING LOOP ---
for target_idx, target in enumerate(pdd_targets):
    # 'target' is a tuple: (section_heading, subheading, subheading_idx, page_num)
    start_marker = target[1]  # The subheading title is our start marker for replacement

    # Determine the end marker to define the section's boundaries
    if target_idx + 1 < len(pdd_targets):
        end_marker = pdd_targets[target_idx + 1][1]
    else:
        # For the last section, use a known final heading like "Appendix". Adjust if your template differs.
        end_marker = "Appendix" 

    # Get the original placeholder text from the template to create the user prompt
    start_loc = find_target_location(target, template_text)
    end_loc = find_target_location(pdd_targets[target_idx + 1], template_text) if target_idx + 1 < len(pdd_targets) else -1
    
    infilling_info = template_text[start_loc:end_loc] if end_loc != -1 else template_text[start_loc:]

    print(f"\n{'='*20}\nProcessing section: {start_marker}\n{'='*20}")
    
    # Assemble prompts for Gemini
    system_prompt = assemble_system_prompt()
    user_prompt = assemble_user_prompt(infilling_info)

    # Ask Gemini for the content, with a few retries for validation
    response = ""
    for i in range(3):  # Retry up to 3 times
        print(f"  > Gemini API Call (Attempt {i+1})...")
        response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
        if is_valid_response(response, infilling_info):
            print("  > Valid response received from Gemini.")
            break
        elif i < 2:
            print("  > Invalid response format, retrying...")
            
    print("\n--- Gemini Response ---")
    print(response)
    print("-----------------------\n")

    # KEY CHANGE: Write the response directly into the correct section of the Word document
    replace_section_in_word_doc(output_path, start_marker, end_marker, response)

    # The input() pause is now just for debugging and does not affect file I/O
    user_input = input("\nPress Enter to continue to the next section, or 'q' to quit: ")
    if user_input.lower() == 'q':
        break

print(f"\nProcessing complete. The final document has been saved at: {output_path}")