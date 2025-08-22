import os
import docx
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


def _iter_block_items(parent):
    """
    A helper function that yields each paragraph and table child within a parent 
    element, in document order. This is crucial for preserving the document's 
    structure.

    Args:
        parent: The parent object, which can be a Document or a table cell (_Cell).

    Yields:
        Paragraph or Table: The block-level items in the document.
    """
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Parent must be a Document or _Cell object")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def load_word_doc_to_string(folder_path):
    """
    Loads text from the first .docx file found in a directory into a single 
    string, preserving the order of paragraphs and tables. Tables are 
    converted into standard Markdown format.

    Args:
        folder_path (str): The path to the directory containing the Word file.

    Returns:
        str: A single string containing the entire text content of the document,
             or an error message if no file is found or cannot be processed.
    """
    # --- 1. Find the first .docx file in the specified folder ---
    filename = None
    try:
        for f in os.listdir(folder_path):
            if f.lower().endswith('.docx'):
                filename = f
                break  # Stop after finding the first .docx file
    except FileNotFoundError:
        return f"Error: Directory not found at '{folder_path}'"

    if not filename:
        return f"Error: No .docx file found in the directory '{folder_path}'"

    # --- 2. Construct the full file path ---
    file_path = os.path.join(folder_path, filename)

    try:
        # --- 3. Open the Word document ---
        document = docx.Document(file_path)
        full_text_blocks = []

        # --- 4. Iterate through all blocks (paragraphs and tables) in order ---
        for block in _iter_block_items(document):
            if isinstance(block, Paragraph):
                # If the block is a paragraph, add its text
                if block.text.strip(): # Avoid adding empty paragraphs
                    full_text_blocks.append(block.text)

            elif isinstance(block, Table):
                # If the block is a table, format it into Markdown
                if not block.rows:
                    continue # Skip empty tables

                table_lines = []
                
                # Process Header Row
                header_cells = [cell.text.replace('\n', ' ').strip() for cell in block.rows[0].cells]
                table_lines.append("| " + " | ".join(header_cells) + " |")

                # Create Separator Line
                num_columns = len(header_cells)
                separator = "| " + " | ".join(['---'] * num_columns) + " |"
                table_lines.append(separator)

                # Process Data Rows
                for row in block.rows[1:]:
                    row_cells = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
                    table_lines.append("| " + " | ".join(row_cells) + " |")
                
                full_text_blocks.append("\n".join(table_lines))

        # --- 5. Join all text blocks into a single string ---
        # Blocks are separated by two newlines for readability.
        return "\n\n".join(full_text_blocks)

    except Exception as e:
        return f"Error processing file '{filename}': {e}"