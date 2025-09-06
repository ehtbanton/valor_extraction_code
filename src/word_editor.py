import docx
import os
import shutil
import json

# --- HELPER FUNCTIONS (UNCHANGED FROM ORIGINAL) ---
def _iter_block_items(parent):
    if isinstance(parent, docx.document.Document): parent_elm = parent.element.body
    elif isinstance(parent, docx.table._Cell): parent_elm = parent._tc
    else: raise ValueError("Parent must be a Document or _Cell object")
    for child in parent_elm.iterchildren():
        if isinstance(child, docx.oxml.text.paragraph.CT_P): yield docx.text.paragraph.Paragraph(child, parent)
        elif isinstance(child, docx.oxml.table.CT_Tbl): yield docx.table.Table(child, parent)

def load_word_doc_to_string(folder_path):
    filename=None;
    try:
        if os.path.isdir(folder_path):
            for f in os.listdir(folder_path):
                if f.lower().endswith('.docx') and not f.startswith('~$'):filename=os.path.join(folder_path, f);break
        elif os.path.isfile(folder_path):filename=folder_path
    except FileNotFoundError:return f"Error: Directory not found at '{folder_path}'"
    if not filename:return f"Error: No .docx file found in '{folder_path}'"
    try:
        doc=docx.Document(filename);blocks=[]
        for block in _iter_block_items(doc):
            if isinstance(block,docx.text.paragraph.Paragraph):
                if block.text.strip():blocks.append(block.text)
            elif isinstance(block,docx.table.Table):
                if not block.rows:continue
                lines=["| "+" | ".join(c.text.replace('\n',' ').strip() for c in block.rows[0].cells)+" |","| "+" | ".join(['---']*len(block.rows[0].cells))+" |"]
                for row in block.rows[1:]:lines.append("| "+" | ".join(c.text.replace('\n',' ').strip() for c in row.cells)+" |")
                blocks.append("\n".join(lines))
        return "\n\n".join(blocks)
    except Exception as e:return f"Error processing file '{os.path.basename(filename)}': {e}"

def create_output_doc_from_template(project_name):
    template_folder,output_folder="output_template","auto_pdd_output"
    template_path=next((os.path.join(template_folder,f) for f in os.listdir(template_folder) if f.lower().endswith('.docx') and not f.startswith('~$')),None)
    if not template_path:raise FileNotFoundError(f"Error: No .docx template found in '{template_folder}'")
    if not os.path.exists(output_folder):os.makedirs(output_folder)
    output_path=os.path.join(output_folder,f"AutoPDD_{project_name}.docx")
    if not os.path.exists(output_path):
        shutil.copy(template_path,output_path);print(f"Created output document at: {output_path}")
    else:
        print(f"Output document already exists at: {output_path}. This file will be updated.")
    return output_path

def add_comment(paragraph, text, author="Source Reference"):
    try:
        # Only add a comment if there is actual sourced content.
        if paragraph.text.strip() and "INFO_NOT_FOUND" not in text and source.strip() != "N/A":
            paragraph.add_comment(text, author=author)
    except Exception:
        pass

# --- THE DEFINITIVE, WORKING SOLUTION ---

def replace_section_in_word_doc(doc_path, start_marker, end_marker, ai_json_data, status):
    try:
        doc = docx.Document(doc_path)
        all_blocks = list(_iter_block_items(doc))

        start_index, end_index = -1, len(all_blocks)
        for i, block in enumerate(all_blocks):
            if isinstance(block, docx.text.paragraph.Paragraph):
                if block.text.strip() == start_marker:
                    start_index = i
                elif start_index != -1 and block.text.strip() == end_marker:
                    end_index = i
                    break
        
        if start_index == -1:
            print(f"  > WARNING: Start marker '{start_marker}' not found.")
            return

        # Fix for section skipping: Find or insert the status paragraph correctly.
        status_p_index = start_index + 1
        if status_p_index < len(all_blocks) and isinstance(all_blocks[status_p_index], docx.text.paragraph.Paragraph) and "SECTION_" in all_blocks[status_p_index].text:
            all_blocks[status_p_index].text = status
        else:
            all_blocks[start_index].insert_paragraph_before(status)
        print(f"  > Status for '{start_marker}' set to: {status}")

        section_blocks = all_blocks[start_index : end_index]

        for block in section_blocks:
            # Handle paragraphs with simple placeholder text
            if isinstance(block, docx.text.paragraph.Paragraph):
                for key, data_obj in ai_json_data.items():
                    if key in block.text and isinstance(data_obj, dict):
                        value = data_obj.get("value", "")
                        source = data_obj.get("source", "N/A")
                        block.text = block.text.replace(key, value)
                        add_comment(block, f"Source: {source}")

            # Handle tables with intelligent key matching
            elif isinstance(block, docx.table.Table):
                headers = [h.text.strip() for h in block.rows[0].cells]
                
                # Logic for simple 2-column key-value tables (e.g., Sectoral Scope)
                if len(headers) == 2:
                    for row in block.rows:
                        label_cell = row.cells[0]
                        value_cell = row.cells[1]
                        label_text = label_cell.text.strip()
                        if label_text in ai_json_data:
                            data = ai_json_data[label_text]
                            value = data.get("value", "")
                            source = data.get("source", "N/A")
                            value_cell.text = value
                            add_comment(value_cell.paragraphs[0], f"Source: {source}")
                
                # Logic for multi-column data tables (e.g., Audit History)
                else:
                    for row in block.rows[1:]: # Skip header row
                        # Get the primary context from the first column of the row
                        row_context = row.cells[0].text.strip()
                        if not row_context or "..." in row_context: continue

                        # Clean up context for better matching (e.g., "Validation/verification" -> "Validation")
                        clean_row_context = row_context.split('/')[0]

                        for i, cell in enumerate(row.cells):
                            # Skip the first cell as it's our context
                            if i == 0: continue
                            
                            header = headers[i]
                            
                            # Find the best matching key from the AI's flat dictionary
                            best_match_key = None
                            for key in ai_json_data:
                                # A key is a match if it contains both the row context and the column header
                                if clean_row_context in key and header in key:
                                    best_match_key = key
                                    break
                            
                            if best_match_key:
                                data = ai_json_data[best_match_key]
                                value = data.get("value", "")
                                source = data.get("source", "N/A")
                                cell.text = value
                                if cell.paragraphs:
                                    add_comment(cell.paragraphs[0], f"Source: {source}")

        doc.save(doc_path)
        print(f"Successfully updated section '{start_marker}' in {os.path.basename(doc_path)}.")

    except Exception as e:
        print(f"FATAL ERROR during document generation for section '{start_marker}': {e}")