
from gemini_interface import ask_gemini
from text_processing import assemble_user_prompt


def refill_section(GEMINI_CLIENT, infilling_info, uploaded_files_cache):
    # Returns a pseudo-response...
    system_prompt = "Search through all user-provided files. In the user prompt, wherever you see 'INFO_NOT_FOUND: <info type>', replace it with the relevant information. Then respond with text identical to the user prompt but with as many replacements made as possible, if you are able to find that info in the provided context. Only respond with this edited user prompt and include no other text in your response."
    user_prompt = assemble_user_prompt(infilling_info)
    print(f"  > Gemini API Call for section refill...")
    response = ask_gemini(GEMINI_CLIENT, user_prompt, system_prompt, uploaded_files_cache)
    return response





