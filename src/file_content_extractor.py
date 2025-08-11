import os
import pdfplumber
import docx
import warnings
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# --- OCR ENGINE SETUP (Requires external installations) ---
# 1. Tesseract-OCR: This engine reads text from images.
#    - Installation: https://github.com/tesseract-ocr/tesseract
#    - For Windows users, you might need to tell pytesseract where you installed Tesseract.
#      Uncomment the line below and set the correct path if you get a "Tesseract not found" error.
#      pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#
# 2. Poppler: This utility converts PDF pages to images for Tesseract to read.
#    - It is a dependency for the 'pdf2image' library.
#    - Installation:
#      - Mac: `brew install poppler`
#      - Linux: `sudo apt-get install poppler-utils`
#      - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/
#                 and extract to a folder like 'C:\poppler-24.02.0'.

def retrieve_all_text(folder_name, poppler_path="C:/poppler"):
    """
    Sequentially goes through all PDF and Word (.docx) files in a folder,
    extracts text using a hybrid approach (standard extraction + OCR for scanned pages),
    and combines it into a single string.

    Args:
        folder_name (str): The path to the folder containing the files.
        poppler_path (str, optional): Path to the Poppler bin directory for Windows users.
                                      Defaults to None.

    Returns:
        str: A single string containing all the text from the files,
             with the content of each file separated by two newline characters.
             Returns an error message if the folder does not exist.
    """
    all_texts = []
    if not os.path.isdir(folder_name):
        return f"Error: The folder '{folder_name}' does not exist."

    print(f"Scanning folder: {folder_name}...")

    for filename in sorted(os.listdir(folder_name)):
        file_path = os.path.join(folder_name, filename)
        if not os.path.isfile(file_path):
            continue

        file_content = ""
        try:
            # --- Process PDF files with hybrid text/OCR extraction ---
            if filename.lower().endswith('.pdf'):
                print(f"  - Processing PDF (with OCR): {filename}")
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()

                        # If text is minimal or non-existent, use OCR
                        if text is None or len(text.strip()) < 100:
                            print(f"    - Page {i+1} has little text, trying OCR...")
                            # Convert the single page to an image, providing the poppler_path
                            images = convert_from_path(
                                file_path,
                                first_page=i+1,
                                last_page=i+1,
                                poppler_path=poppler_path
                            )
                            if images:
                                ocr_text = pytesseract.image_to_string(images[0])
                                file_content += ocr_text + "\n"
                        else:
                            file_content += text + "\n"

            # --- Process Word (.docx) files ---
            elif filename.lower().endswith('.docx'):
                print(f"  - Extracting text from DOCX: {filename}")
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    file_content += para.text + "\n"

            if file_content:
                all_texts.append(file_content.strip())

        except Exception as e:
            print(f"    [!] Could not process file '{filename}'.")
            print(f"    Reason: {type(e).__name__} - {e}")

    print("Extraction complete.")
    return "\n\n".join(all_texts)
