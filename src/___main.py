# Welcome to AutoPDD!

# Todo list:
# - Fill in basic functionality (see detailed comments in this file)
# - Check possibility of using somebody's MCP protocol for LLM processing inputs/outputs
# - Add required library imports and auto loading
# - Trial ways of a) using text processing ONLY rather than giving Gemini the PDFs, and b) using lower context lengths.

import os

from gemini_interface import setup_gemini, ask_gemini
from file_manager import name_files_in_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location#, assemble_user_prompt, assemble_system_prompt, is_valid_response
from template_text_loader import load_word_doc_to_string

template_text = load_word_doc_to_string("output_template") #loads from folder
#print(f"Template text:\n\n{template_text}")

contents_list = retrieve_contents_list(template_text)
#print("Contents List:\n" + contents_list)

pdd_targets = get_pdd_targets(contents_list) # should be an array of tuples containing (section_heading, subheading, subheading_idx, page_num)
print("PDD Targets:" + str(pdd_targets))

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

    # Create a detailed system prompt for the LLM. Defines an interpretable text-based format which aligns with the template. This should be the same for the input and output.
    system_prompt = assemble_system_prompt(infilling_info)
    
    # Create a user prompt (should just contain text info correspoding to the current subheading as provided). Make sure it's in the right format as per the system prompt!
    user_prompt = assemble_user_prompt(target, infilling_info)

    response = "" # initializing
    for i in range(10): # Retry up to 10 times before giving up
        response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, provided_files_list)
        # It should be a PRECISELY STRUCTURED RESPONSE. Make sure to allow it to also say it wasn't able to find the relevant info!
        # Check if the response is the correct format/structure. If it isn't, try again.
        if is_valid_response(response, infilling_info):
            break

    # Fill in this part of the output word doc. (May need to say the relevant info couldn't be found).
    fill_in_output_doc(target, infilling_info, response)


# ... that should be all for now ...

