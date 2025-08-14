import os

from llama_interface import setup_llama, ask_llama
from gemini_interface import setup_gemini, ask_gemini
from file_content_extractor import retrieve_all_text
from text_processing import retrieve_contents_list, get_pdd_targets


# Adjust model path and parameters as needed

#model_path = "F:\\_llm_models\\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" # Meta Llama 3.1 8B model
#model_path = "F:\\_llm_models\\Qwen3-32B-Q4_K_M.gguf" # qwen 3 reasoning model
#LLAMA_CLIENT = setup_llama(model_path, n_gpu_layers=-1, n_ctx=10000)


template_text = retrieve_all_text("output_template")
contents_list = retrieve_contents_list(template_text)
#print("Contents List:\n" + contents_list)


provided_files_list = os.listdir("provided_documents/prime_road")
for i,file in  enumerate(provided_files_list):
    provided_files_list[i] = "provided_documents/prime_road/" + file


GEMINI_CLIENT = setup_gemini()
# Create a comprehensive system prompt
system_prompt = """You are a technical document analyst specializing in renewable energy projects and environmental documentation. Your task is to extract specific, accurate information from project documents.

INSTRUCTIONS:
1. Read all provided documents carefully
2. Extract factual information only - do not infer or assume details not explicitly stated
3. For location information, provide specific geographic details including coordinates if available
4. For technical specifications, include exact numbers, units, and measurements
5. If information is not found in the documents, explicitly state "Information not found in provided documents"
6. Organize your response with clear headings and bullet points
7. Cite specific document sections when possible

FOCUS AREAS:
- Project location (coordinates, address, administrative boundaries)
- Technical specifications (capacity, technology type, equipment)
- Environmental impact details
- Timeline and development phases
- Stakeholder information
- Regulatory and permitting details"""

# Create a more structured and specific prompt
user_prompt = """Based on the uploaded project documents, please provide a comprehensive analysis with the following information:

1. PROJECT LOCATION:
   - Exact geographic location (coordinates, address)
   - Administrative boundaries (province, district, municipality)
   - Land area and boundaries

2. TECHNICAL SPECIFICATIONS:
   - Project capacity (MW, MWac, MWdc)
   - Technology type and specifications
   - Key equipment and infrastructure

3. PROJECT DETAILS:
   - Project name and developer
   - Development timeline
   - Investment amount and funding

4. ENVIRONMENTAL ASPECTS:
   - Environmental impact assessment findings
   - Mitigation measures
   - Social and community considerations

Please structure your response clearly and cite which documents contain each piece of information."""

# Make the API call with system prompt
response_text = ask_gemini(
    GEMINI_CLIENT, 
    user_prompt, 
    file_paths=provided_files_list,
    system_prompt=system_prompt
)

print("\n" + "="*80)
print("GEMINI ANALYSIS RESULTS")
print("="*80)
print(response_text)

#provided_docs_text = retrieve_all_text("provided_documents/prime_road")
#print("Provided Docs Text:\n" + provided_docs_text)



# Use the contents list fromt the template to set some targets for information to find from provided docs
# It's an array containing tuples of (heading, subheading title, subheading idx, page num)
#pdd_targets = get_pdd_targets(contents_list)


        
