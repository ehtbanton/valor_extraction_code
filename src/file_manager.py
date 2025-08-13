
import os
import PyPDF2
import docx

def extract_text_from_folder(folder_path):
    """
    Extracts text from all PDF and Word (.docx) files in a given folder.

    Args:
        folder_path (str): The absolute or relative path to the folder 
                           containing the files.

    Returns:
        dict: A dictionary where keys are filenames and values are the 
              extracted text content from those files.
              Returns an empty dictionary if the folder does not exist or is empty.
    """
    # Check if the provided path is a valid directory
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'")
        return {}

    extracted_texts = {}
    print(f"Scanning folder: {folder_path}")

    # Iterate over each file in the specified directory
    for filename in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)

        # Skip subdirectories
        if not os.path.isfile(file_path):
            continue

        text = ""
        try:
            # --- Handle PDF files ---
            if filename.lower().endswith('.pdf'):
                print(f"-> Found PDF: {filename}")
                with open(file_path, 'rb') as pdf_file:
                    # Create a PDF reader object
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    # Loop through each page and extract text
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() or "" # Add "" if None
                extracted_texts[filename] = text
                print(f"   ...extracted {len(text)} characters.")

            # --- Handle Word (.docx) files ---
            elif filename.lower().endswith('.docx'):
                print(f"-> Found DOCX: {filename}")
                # Create a Document object
                doc = docx.Document(file_path)
                # Loop through each paragraph and extract text
                full_text = [para.text for para in doc.paragraphs]
                text = '\n'.join(full_text)
                extracted_texts[filename] = text
                print(f"   ...extracted {len(text)} characters.")

        except Exception as e:
            # Handle potential errors with file processing
            print(f"Could not process file '{filename}'. Reason: {e}")

    return extracted_texts



def name_files_in_folder(folder_path):
    provided_files_list = os.listdir(folder_path)
    for file in provided_files_list:
        provided_files_list[provided_files_list.index(file)] = folder_path + "/" + file
    return provided_files_list













