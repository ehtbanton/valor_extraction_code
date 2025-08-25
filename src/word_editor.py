import docx
import os
import shutil
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
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







def create_output_doc_from_template(project_name):
    """
    Creates a new Word document for output by copying the template.
    If the output file already exists, it does nothing, ensuring a single file is used.
    
    Args:
        project_name (str): The name of the project to be used in the output filename.

    Returns:
        str: The path to the output document.
    """
    template_folder = "output_template"
    output_folder = "auto_pdd_output"
    template_path = ""
    output_path = os.path.join(output_folder, f"AutoPDD_{project_name}.docx")

    # Find the template file in the specified folder
    for f in os.listdir(template_folder):
        if f.lower().endswith('.docx') and not f.startswith('~$'):
            template_path = os.path.join(template_folder, f)
            break
    
    if not template_path:
        raise FileNotFoundError(f"Error: No .docx template found in '{template_folder}'")

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Copy the template to the output destination only if the output file doesn't already exist
    if not os.path.exists(output_path):
        shutil.copy(template_path, output_path)
        print(f"Created output document at: {output_path}")
    else:
        print(f"Output document already exists at: {output_path}. This file will be updated.")
        
    return output_path

def _iter_block_items(parent):
    """Helper function to yield each paragraph and table within a parent element."""
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

def _delete_element(element):
    """Removes a paragraph or table element from the document."""
    el = element._element
    el.getparent().remove(el)

def parse_markdown_table(markdown_text):
    """Parses a Markdown table string into a header and a list of row data."""
    lines = [line.strip() for line in markdown_text.strip().split('\n')]
    if len(lines) < 2:  # Header and separator line are minimum
        return None, None
    
    # Clean lines by removing leading/trailing pipes
    cleaned_lines = [line[1:-1] if line.startswith('|') and line.endswith('|') else line for line in lines]
    
    # Split each row into cells
    table_data = [[cell.strip() for cell in row.split('|')] for row in cleaned_lines]
    
    header = table_data[0]
    rows = table_data[2:]  # Skip the separator line
    return header, rows

def replace_section_in_word_doc(doc_path, start_marker, end_marker, new_content_str):
    """
    Replaces the content between two heading markers in a Word document.
    
    Args:
        doc_path (str): Path to the .docx file to be modified.
        start_marker (str): The text of the heading where the section to be replaced begins.
        end_marker (str): The text of the heading where the section ends.
        new_content_str (str): The new content (from Gemini) to be inserted.
    """
    doc = docx.Document(doc_path)
    
    in_section_to_replace = False
    elements_to_delete = []
    insert_after_element = None

    # First, find the elements that need to be deleted
    all_elements = list(_iter_block_items(doc))
    for element in all_elements:
        if isinstance(element, Paragraph):
            # If we find the end marker, stop collecting elements for deletion
            if element.text.strip() == end_marker.strip():
                in_section_to_replace = False
            
            # If we are in the target section, add the element to the deletion list
            if in_section_to_replace:
                elements_to_delete.append(element)

            # If we find the start marker, start collecting elements from the next one
            if element.text.strip() == start_marker.strip():
                in_section_to_replace = True
                insert_after_element = element
        elif in_section_to_replace: # If it's a table within the section
            elements_to_delete.append(element)
    
    if insert_after_element is None:
        print(f"Warning: Start marker '{start_marker}' not found. Cannot update section.")
        return

    # Delete the old placeholder elements
    for element in elements_to_delete:
        _delete_element(element)

    # Now, insert the new content from the Gemini response
    current_element_xml = insert_after_element._element 
    
    # Split the new content into blocks (paragraphs or tables)
    content_blocks = new_content_str.strip().split('\n\n')

    for block in content_blocks:
        block = block.strip()
        if not block:
            continue

        # Check if the block is a Markdown table
        if block.startswith('|') and '|' in block:
            header, rows = parse_markdown_table(block)
            if header and rows:
                num_cols = len(header)
                table = doc.add_table(rows=1, cols=num_cols)
                table.style = 'Table Grid'
                for i, col_name in enumerate(header):
                    table.cell(0, i).text = col_name
                for row_data in rows:
                    row_cells = table.add_row().cells
                    for i, cell_text in enumerate(row_data):
                        if i < num_cols:
                            row_cells[i].text = cell_text
                current_element_xml.addnext(table._element)
                current_element_xml = table._element
            else: # If parsing fails, treat it as a plain paragraph
                p = docx.oxml.shared.OxmlElement('w:p')
                docx.text.paragraph.Paragraph(p, doc).text = block
                current_element_xml.addnext(p)
                current_element_xml = p
        else: # It's a regular paragraph
            p = docx.oxml.shared.OxmlElement('w:p')
            docx.text.paragraph.Paragraph(p, doc).text = block
            current_element_xml.addnext(p)
            current_element_xml = p
            
    doc.save(doc_path)
    print(f"Successfully updated section: '{start_marker}'")


    