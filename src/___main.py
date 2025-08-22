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

from gemini_interface import setup_gemini, ask_gemini, upload_files_to_gemini
from file_manager import name_files_in_folder, extract_text_from_folder
from text_processing import retrieve_contents_list, get_pdd_targets, find_target_location, assemble_system_prompt, assemble_user_prompt, is_valid_response
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
#provided_files_list = name_files_in_folder(f"provided_documents/{project_name}")
all_provided_text = extract_text_from_folder(f"provided_documents/{project_name}")



GEMINI_CLIENT = setup_gemini()
uploaded_files_cache = upload_files_to_gemini([f"provided_documents/{project_name}/provided_docs.txt"])

for target_idx,target in enumerate(pdd_targets):
    # Find location of target in word file. Use the python-docx library.
    # Retrieve specific instructions and infilling info (e.g. is a table present?).
    start_loc = find_target_location(target, template_text)
    end_loc = find_target_location(pdd_targets[target_idx+1], template_text)
    infilling_info = template_text[start_loc:end_loc]
    #print(f"\n\nInfilling Info for {target}:\n\n {infilling_info}")

    system_prompt = assemble_system_prompt()
    #print(f"\n\nSystem Prompt:\n{system_prompt}")
    user_prompt = assemble_user_prompt(infilling_info)
    #print(f"\n\nUser Prompt:\n{user_prompt}")

    response = "" # initializing
    for i in range(10): # Retry up to 10 times before giving up
        response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
        # It should be a PRECISELY STRUCTURED RESPONSE. Make sure to allow it to also say it wasn't able to find the relevant info!
        # Check if the response is the correct format/structure. If it isn't, try again.
        if is_valid_response(response, infilling_info):
            break
    print(f"Response:\n\n{response}")

    input() # so we don't run through the whole template for now to save api credits...

    # Fill in this part of the output word doc. (May need to say the relevant info couldn't be found).
    output_path = f"auto_pdd_output/AutoPDD_{project_name}.docx"
    #fill_in_output_doc(target, infilling_info, response)


# ... that should be all for now ...

