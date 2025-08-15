# Welcome to AutoPDD!

# Todo list:
# - Fill in basic functionality (see detailed comments in this file).
#       WE ARE HERE. Current status: 
#                    - Table interpretation is broken. Consider giving more rigid specific structural understanding in system prompt.
#                      (i.e. make multiple versions of the system prompt to deal with different situations)
#                    - May also be helpful to change how template info is provided as this may make creating specific system prompts easier.
#                      e.g. other text formats/direct word doc snippets/screenshots could be trialled, or just using shorter chunks of text
#                      (like just a table rather than whole subheading section). Be mindful that we want to EVENTUALLY move to text-only.
# - Check possibility of using somebody's MCP protocol for LLM processing inputs/outputs
# - Add required library imports and auto loading
# - For later: Trial ways of a) using text processing ONLY rather than giving Gemini the PDFs, and b) using lower context lengths. Then trial local LLMs.

import os
import time
from gemini_interface import setup_gemini, ask_gemini
from file_manager import name_files_in_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location, assemble_system_prompt, assemble_user_prompt, is_valid_response, create_followup_prompt, count_missing_fields, merge_followup_response
from template_text_loader import load_word_doc_to_string#, fill_in_output_doc


os.system('cls' if os.name == 'nt' else 'clear')

template_text = load_word_doc_to_string("output_template") #loads from folder
#print(f"Template text:\n\n{template_text}")

contents_list = retrieve_contents_list(template_text)
#print("Contents List:\n" + contents_list)

### CONSIDER CHANGING if more granularity seems helpful ###
pdd_targets = get_pdd_targets(contents_list) # should be an array of tuples containing (section_heading, subheading, subheading_idx, page_num)
#print("PDD Targets:" + str(pdd_targets))

project_name = "prime_road"
provided_files_list = name_files_in_folder(f"provided_documents/{project_name}")
output_path = f"auto_pdd_output/AutoPDD_{project_name}.docx"

GEMINI_CLIENT = setup_gemini()




for target_idx,target in enumerate(pdd_targets):
    # Find location of target in word file. Use the python-docx library.
    # Retrieve specific instructions and infilling info (e.g. is a table present?).
    start_loc = find_target_location(target, template_text)
    end_loc = find_target_location(pdd_targets[target_idx+1], template_text)
    infilling_info = template_text[start_loc:end_loc]
    
    system_prompt = assemble_system_prompt()
    user_prompt = assemble_user_prompt(infilling_info)

    response = ""
    # Primary search attempt
    for i in range(10):
        response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, provided_files_list)
        if is_valid_response(response, infilling_info):
            break
    
    # Check for missing information and do targeted follow-up
    missing_count = count_missing_fields(response)
    if missing_count > 0:
        print(f"Found {missing_count} missing fields, performing targeted search...")
        
        followup_prompt = create_followup_prompt(response, infilling_info)
        if followup_prompt:
            # Attempt follow-up search
            followup_response = ask_gemini(GEMINI_CLIENT, followup_prompt, system_prompt, provided_files_list)
            print(f"Follow-up search completed.")
            
            # Try to merge findings back into original response
            original_missing = missing_count
            updated_response = merge_followup_response(response, followup_response)
            new_missing = count_missing_fields(updated_response)
            
            if new_missing < original_missing:
                print(f"Follow-up successful: reduced missing fields from {original_missing} to {new_missing}")
                response = updated_response
            else:
                print(f"Follow-up did not find additional information")
            
            print(f"\nFollow-up details:\n{followup_response}")
    
    print(f"\n\n\nFinal Response:\n\n{response}")
    input() # so we don't run through the whole template for now to save api credits...

    # Fill in this part of the output word doc. (May need to say the relevant info couldn't be found).
    #fill_in_output_doc(target, infilling_info, response)


# ... that should be all for now ...

