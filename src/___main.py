# Welcome to AutoPDD!

# Todo list:
# - Fill in basic functionality (see detailed comments in this file)
# - Check possibility of using somebody's MCP protocol for LLM processing inputs/outputs
# - Add required library imports and auto loading
# - Trial ways of a) using text processing ONLY rather than giving Gemini the PDFs, and b) using lower context lengths.

from gemini_interface import setup_gemini, ask_gemini
from file_manager import extract_text_from_folder, name_files_in_folder
from text_processing import retrieve_contents_list, get_pdd_targets
# from word_editor 

template_text = extract_text_from_folder("output_template")
contents_list = retrieve_contents_list(template_text)
#print("Contents List:\n" + contents_list)
# Get "PDD targets" from the contents list. One PDD target per subheading.
pdd_targets = get_pdd_targets(contents_list) # should be an array of tuples containing (section_heading, subheading, subheading_idx, page_num)
#print("PDD Targets:" + str(pdd_targets))



provided_files_list = name_files_in_folder("provided_documents/prime_road")
GEMINI_CLIENT = setup_gemini()

# Make a new named copy of the template in the auto_pdd_output folder. Name it after the folder name in provided_documents (e.g. here use "AutoPDD_prime_road.docx")

for target in pdd_targets:
    
    # Find location of target in word file. Use the python-docx library.

    # Retrieve specific instructions and infilling info (e.g. is a table present?).

    # Create a detailed system prompt for the LLM. 
    # It should be able to COMPLETELY produce the required text/table at this point in the word doc, using an interpretable format which aligns with the template.
    
    # Create a user prompt (should just contain text info correspoding to the current subheading as provided)

    # Loop:
        # Prompt the LLM using the CLIENT, user prompt, system prompt, and folder dir of all relevant company files.
        # It should be a PRECISELY STRUCTURED RESPONSE. Make sure to allow it to also say it wasn't able to find the relevant info!
        # response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, provided_files_list)

        # Check if the response is the correct format/structure. If it isn't, try again. Repeat up to 10 times?

    # Fill in this part of the output word doc. (May need to say the relevant info couldn't be found).



# ... that should be all for now ...


        
