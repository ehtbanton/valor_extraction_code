import os

from llama_interface import setup_llama, ask_llama
from gemini_interface import setup_gemini, ask_gemini
from file_content_extractor import retrieve_all_text
from text_processing import retrieve_contents_list, get_pdd_targets


# Adjust model path and parameters as needed
model_path = "F:\\_llm_models\\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" # Meta Llama 3.1 8B model
#model_path = "F:\\_llm_models\\Qwen3-32B-Q4_K_M.gguf" # qwen 3 reasoning model
#LLAMA_CLIENT = setup_llama(model_path, n_gpu_layers=-1, n_ctx=10000)


template_text = retrieve_all_text("output_template")
contents_list = retrieve_contents_list(template_text)
#print("Contents List:\n" + contents_list)


provided_files_list = os.listdir("provided_documents/prime_road")
for file in provided_files_list:
    provided_files_list[provided_files_list.index(file)] = "provided_documents/prime_road/" + file


GEMINI_CLIENT = setup_gemini()
prompt="Where is the 60 MW alternating current (MWac) utility-scale solar photovoltaic (PV) power project located? What else can you tell me about it?"
response_text = ask_gemini(GEMINI_CLIENT, prompt, file_paths=provided_files_list)

print("\n\n")
print(response_text)

#provided_docs_text = retrieve_all_text("provided_documents/prime_road")
#print("Provided Docs Text:\n" + provided_docs_text)



# Use the contents list fromt the template to set some targets for information to find from provided docs
# It's an array containing tuples of (heading, subheading title, subheading idx, page num)
#pdd_targets = get_pdd_targets(contents_list)


        
