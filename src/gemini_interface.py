import os
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

def ask_gemini(
    agent: genai.GenerativeModel,
    prompt: str,
    system_prompt: Optional[str] = None,
    file_paths: Optional[List[str]] = None
) -> str:
    """
    Sends a prompt, an optional system prompt, and a list of files to the 
    initialized Gemini agent and gets a response.

    Args:
        agent (genai.GenerativeModel): The initialized generative model agent.
        prompt (str): The text prompt to send to the model.
        system_prompt (Optional[str]): An optional system prompt to guide the 
                                       model's behavior. Defaults to None.
        file_paths (Optional[List[str]]): A list of paths to the files to be sent. 
                                          Defaults to None.

    Returns:
        str: The text part of the model's response. Returns an error
             message if the agent is not valid or an error occurs.
    """
    if not agent:
        return "Error: Gemini agent is not initialized. Please run setup_gemini() successfully."

    # --- New: Combine system prompt with user prompt ---
    # If a system prompt is provided, it's prepended to the main prompt 
    # to guide the model's overall response.
    full_prompt = f"{system_prompt}\n\n---\n\n{prompt}" if system_prompt else prompt
    # --- End of new section ---

    # Prepare content list with the full prompt and any files
    content = [full_prompt]
    uploaded_files = []

    if file_paths:
        print(f"\nUploading {len(file_paths)} file(s)...")
        for file_path in file_paths:
            try:
                # Upload the file and get a file handle
                uploaded_file = genai.upload_file(path=file_path)
                uploaded_files.append(uploaded_file)
                print(f"Successfully uploaded {file_path}")
            except Exception as e:
                # If a file fails to upload, notify the user and skip it.
                print(f"Failed to upload {file_path}: {e}")
    
    # Add the uploaded files to the content list for the API call
    content.extend(uploaded_files)

    try:
        # Get the response from the model
        print("Generating content from prompt and files...\n")
        response = agent.generate_content(content)
        return response.text
    except Exception as e:
        return f"An error occurred while asking Gemini: {e}"








