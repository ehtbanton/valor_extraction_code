import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import mimetypes
from typing import List, Optional


def setup_gemini():
    """
    Configures the Gemini API with an API key from environment variables
    and initializes the generative model.

    This function expects the API key to be set in an environment variable
    named 'GOOGLE_API_KEY', which can be loaded from a .env file.

    Returns:
        genai.GenerativeModel: An initialized generative model agent
                               ready to generate content.
    """
    try:
        # Get the API key from the environment variable.
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Make sure to create a .env file with GOOGLE_API_KEY='your_key'.")

        # Configure the generative AI client
        genai.configure(api_key=api_key)

        # Create the model. 'gemini-1.5-flash' is a powerful multimodal model.
        agent = genai.GenerativeModel('gemini-2.5-flash')
        return agent
    except Exception as e:
        print(f"An error occurred during setup: {e}")
        return None

def ask_gemini(agent: genai.GenerativeModel, prompt: str, system_prompt: str = None, file_paths: Optional[List[str]] = None, max_upload_retries: int = 3) -> str:
    """
    Note: I reordered parameters to match your main.py call pattern
    """
    if not agent:
        return "Error: Gemini agent is not initialized."
    
    complete_prompt = ""
    if system_prompt:
        complete_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER QUERY:\n{prompt}"
    else:
        complete_prompt = prompt
    
    content = [complete_prompt]
    uploaded_files = []
    
    if file_paths:
        print(f"Uploading {len(file_paths)} file(s)...")
        for file_path in file_paths:
            success = False
            for attempt in range(max_upload_retries):
                try:
                    uploaded_file = genai.upload_file(path=file_path)
                    uploaded_files.append(uploaded_file)
                    print(f"Successfully uploaded {file_path}")
                    success = True
                    break
                except Exception as e:
                    print(f"Upload attempt {attempt + 1} failed for {file_path}: {e}")
                    if attempt < max_upload_retries - 1:
                        time.sleep(2)  # Wait before retry
            
            if not success:
                print(f"FAILED to upload {file_path} after {max_upload_retries} attempts")
        
        content.extend(uploaded_files)
    
    try:
        print("Generating content from prompt and files...")
        response = agent.generate_content(content)
        return response.text
    except Exception as e:
        return f"An error occurred while asking Gemini: {e}"








