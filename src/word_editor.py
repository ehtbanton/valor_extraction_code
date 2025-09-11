import docx
import os
import shutil
import json
import re

# --- HELPER FUNCTIONS ---
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

def get_value_for_key_pattern(ai_json_data, patterns):
    """Helper to find value matching any of the patterns."""
    for pattern in patterns:
        for key, data in ai_json_data.items():
            if pattern.lower() in key.lower():
                value = data.get("value", "")
                if value and value != "INFO_NOT_FOUND":
                    return value
    return None

def replace_section_in_word_doc(doc_path, start_marker, end_marker, ai_json_data, status):
    """Ultra-simple direct replacement approach."""
    try:
        doc = docx.Document(doc_path)
        
        # First, insert or update status - find and update/add only once
        found_section = False
        status_updated = False
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            text_clean = text.replace('\t', ' ')
            start_clean = start_marker.strip()
            
            # Use flexible matching like in the processing section
            if (text_clean == start_clean or 
                text_clean.startswith(start_clean + ' ') or
                text_clean.startswith(start_clean + '\t') or
                start_clean in text_clean):
                found_section = True
                print(f"  > Found section header: '{text}'")
                
                # Check if next paragraph already has status
                if i + 1 < len(doc.paragraphs):
                    next_para = doc.paragraphs[i + 1]
                    if "SECTION_" in next_para.text:
                        next_para.text = status
                        status_updated = True
                        print(f"  > Updated existing status to: {status}")
                
                if not status_updated:
                    # For now, just skip adding new status - focus on content replacement
                    print(f"  > Status not found to update, but continuing with processing")
                break
        
        if not found_section:
            print(f"  > WARNING: Section '{start_marker}' not found")
            return
        
        print(f"  > Processing '{start_marker}' - Status: {status}")
        
        # Now process content based on section type
        in_section = False
        
        # Process paragraphs - need to skip Contents/TOC and find actual content section
        passed_project_details = False
        for paragraph in doc.paragraphs:
            text = paragraph.text
            
            # Check if we've passed the main "Project Details" section (after TOC)
            if not passed_project_details:
                if text.strip() == "Project Details" and "Contents" not in text:
                    passed_project_details = True
                    print("  > Passed Contents section, now looking for actual content")
                continue
            
            # More flexible section matching (handle tabs and page numbers)
            text_clean = text.strip().replace('\t', ' ')
            start_clean = start_marker.strip()
            end_clean = end_marker.strip()
            
            # Extract just the title for matching actual content sections
            start_title = start_clean.split(' ', 1)[1] if ' ' in start_clean else start_clean
            end_title = end_clean.split(' ', 1)[1] if ' ' in end_clean else end_clean
            
            # Try different matching patterns - prioritize standalone titles
            if (text_clean == start_title):  # Match just the title (actual content section)
                in_section = True
                print(f"  > Found section start: '{text.strip()}'")
                continue
            elif (text_clean == end_title):  # Match just the title
                in_section = False
                print(f"  > Found section end: '{text.strip()}'")
                break
            
            if not in_section:
                continue
            
            # Skip status paragraphs
            if "SECTION_" in text:
                continue
            
            # HANDLE CHECKBOXES SPECIFICALLY (text-based since template uses form controls)
            if (any(word in text.lower() for word in ["single location", "multiple locations", "grouped project"]) and
                len(text.strip()) < 100):  # Short checkbox-like text
                
                # Get the checkbox value from AI - try multiple patterns
                checkbox_value = get_value_for_key_pattern(ai_json_data, ["checkbox", "project design", "design"])
                
                print(f"    > Found potential checkbox text: '{text.strip()}'")
                print(f"    > Checkbox value from AI: '{checkbox_value}'")
                
                if checkbox_value:
                    # More flexible pattern matching
                    checkbox_lower = checkbox_value.lower()
                    text_lower = text.lower()
                    
                    # Check for single location/installation
                    if ("single" in checkbox_lower) and "single" in text_lower:
                        paragraph.text = f"[X] {text.strip()}"
                        print(f"    > [X] Selected: Single location - {checkbox_value}")
                    # Check for multiple locations (not grouped)  
                    elif ("multiple" in checkbox_lower and "group" not in checkbox_lower) and ("multiple" in text_lower and "group" not in text_lower):
                        paragraph.text = f"[X] {text.strip()}"
                        print(f"    > [X] Selected: Multiple locations - {checkbox_value}")
                    # Check for grouped project
                    elif ("group" in checkbox_lower or "grouped" in checkbox_lower) and "group" in text_lower:
                        paragraph.text = f"[X] {text.strip()}"
                        print(f"    > [X] Selected: Grouped project - {checkbox_value}")
                    else:
                        print(f"    > [X] No checkbox match found for: '{checkbox_value}' in text: '{text.strip()[:50]}...'")
                else:
                    print(f"    > [X] No checkbox value found in AI response")
                    # Debug: show all available keys
                    print(f"    > Available AI keys: {list(ai_json_data.keys())[:5]}")
            
            # HANDLE BULLET POINTS (SECTION 1.1)
            elif text.strip().startswith('•') or text.strip().startswith('·'):
                # Map bullet content by looking for specific patterns
                filled = False
                
                if ("technologies" in text.lower() or "measures" in text.lower()) and not filled:
                    value = get_value_for_key_pattern(ai_json_data, ["bullet: technolog", "bullet: measures", "technolog", "measures"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = f"• {value}"
                        print(f"    > Filled: Technologies bullet")
                        filled = True
                
                if ("location" in text.lower()) and not filled:
                    value = get_value_for_key_pattern(ai_json_data, ["bullet: location", "location"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = f"• {value}"
                        print(f"    > Filled: Location bullet")
                        filled = True
                
                if ("ghg" in text.lower() or "emission" in text.lower()) and not filled:
                    value = get_value_for_key_pattern(ai_json_data, ["bullet: ghg", "bullet: emission", "ghg", "emission"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = f"• {value}"
                        print(f"    > Filled: GHG emissions bullet")
                        filled = True
                
                if ("scenario" in text.lower() or "prior" in text.lower()) and not filled:
                    value = get_value_for_key_pattern(ai_json_data, ["bullet: scenario", "bullet: prior", "scenario", "prior"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = f"• {value}"
                        print(f"    > Filled: Prior scenario bullet")
                        filled = True
                
                if ("estimate" in text.lower() or "annual" in text.lower()) and not filled:
                    value = get_value_for_key_pattern(ai_json_data, ["bullet: annual", "bullet: estimate", "annual", "estimate", "reduction"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = f"• {value}"
                        print(f"    > Filled: Estimates bullet")
                        filled = True
                
                # If no specific match, try generic bullet patterns
                if not filled:
                    for key, data in ai_json_data.items():
                        if key.lower().startswith("bullet:") and data.get("value") != "INFO_NOT_FOUND":
                            paragraph.text = f"• {data.get('value')}"
                            print(f"    > Filled: Generic bullet - {key}")
                            break
            
            # HANDLE PARAGRAPH CONTENT REPLACEMENT - be more careful to avoid duplication
            elif (any(keyword in text.lower() for keyword in ["describe", "justify", "explain", "provide", "details", "information"]) and
                  not text.strip().startswith('•') and len(text.strip()) > 20):  # Avoid short lines and bullets
                
                # Try to find relevant content based on AI response structure
                replaced = False
                
                # Main summary description paragraph  
                if "summary description" in text.lower() and "project" in text.lower():
                    # This is the main instruction paragraph, replace with summary content
                    summary_text = ""
                    for key, data in ai_json_data.items():
                        if "paragraph:" in key.lower() and data.get("value") != "INFO_NOT_FOUND":
                            if summary_text:
                                summary_text += "\n\n"
                            summary_text += data.get("value", "")
                    
                    if summary_text:
                        paragraph.text = summary_text
                        print(f"    > Filled: Main summary paragraph with combined content")
                        replaced = True
                
                # General eligibility paragraphs
                elif "general eligibility" in text.lower() or ("projects, describe and justify" in text.lower()):
                    value = get_value_for_key_pattern(ai_json_data, ["paragraph: general eligibility", "general eligibility"])
                    if value and value != "INFO_NOT_FOUND":
                        paragraph.text = value
                        print(f"    > Filled: General eligibility paragraph")
                        replaced = True
                
                # Other instruction paragraphs - try to match with any available paragraph data
                if not replaced:
                    # Look for any paragraph data that might match this instruction
                    for key, data in ai_json_data.items():
                        if ("paragraph:" in key.lower() and 
                            data.get("value") != "INFO_NOT_FOUND" and
                            len(data.get("value", "")) > 50):  # Non-trivial content
                            paragraph.text = data.get("value")
                            print(f"    > Filled: Instruction paragraph with {key}")
                            replaced = True
                            break
                
                if not replaced:
                    print(f"    > No specific content found for paragraph: '{text.strip()[:50]}...'")
        
        # Process tables - need to track section boundaries properly
        current_tables_in_section = []
        
        # First pass: identify which tables are in our section - skip Contents/TOC
        passed_project_details = False
        in_section = False
        for block in _iter_block_items(doc):
            if isinstance(block, docx.text.paragraph.Paragraph):
                text = block.text.strip()
                
                # Check if we've passed the main "Project Details" section (after TOC)
                if not passed_project_details:
                    if text == "Project Details" and "Contents" not in text:
                        passed_project_details = True
                    continue
                
                # Extract just the title for matching actual content sections
                start_title = start_marker.split(' ', 1)[1] if ' ' in start_marker else start_marker
                end_title = end_marker.split(' ', 1)[1] if ' ' in end_marker else end_marker
                
                # Use same flexible matching as paragraph processing
                if text == start_title:
                    in_section = True
                    print(f"      > Table processing: Found section start: '{text}'")
                elif text == end_title:
                    in_section = False
                    print(f"      > Table processing: Found section end: '{text}'")
                    break
            elif isinstance(block, docx.table.Table) and in_section:
                current_tables_in_section.append(block)
                print(f"      > Found table with {len(block.rows)} rows in section")
        
        # Second pass: process only tables that are in our section
        for table in current_tables_in_section:
            
            if len(table.rows) < 2:
                continue
            
            # Get headers
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            print(f"    > Found table with headers: {headers}")
            
            # Process data rows
            for row_idx in range(1, len(table.rows)):
                row = table.rows[row_idx]
                
                # Get row label (first cell)
                row_label = row.cells[0].text.strip() if row.cells else ""
                
                # Process each data cell
                for col_idx in range(len(row.cells)):
                    cell = row.cells[col_idx]
                    
                    # Skip the first column (row labels) unless it's completely empty
                    if col_idx == 0:
                        continue
                    
                    # Determine if cell needs filling (has placeholder or is empty)
                    needs_filling = (
                        not cell.text.strip() or 
                        '...' in cell.text or 
                        '…' in cell.text or
                        cell.text.strip() in ['', ' ', 'One year']
                    )
                    
                    if not needs_filling:
                        continue
                    
                    # Get column header
                    col_header = headers[col_idx] if col_idx < len(headers) else ""
                    
                    # Try to fill with AI data
                    filled = False
                    
                    # AUDIT HISTORY TABLE (Section 1.2)
                    if "validation" in row_label.lower() and col_header:
                        if "period" in col_header.lower():
                            value = get_value_for_key_pattern(ai_json_data, ["table: validation", "validation period", "period"])
                            if value and value != "INFO_NOT_FOUND":
                                cell.text = value
                                print(f"      > Filled: Validation Period = {value}")
                                filled = True
                        elif "program" in col_header.lower():
                            value = get_value_for_key_pattern(ai_json_data, ["table: program", "validation program", "program"])
                            if value and value != "INFO_NOT_FOUND":
                                cell.text = value
                                print(f"      > Filled: Program = {value}")
                                filled = True
                        elif "body name" in col_header.lower():
                            value = get_value_for_key_pattern(ai_json_data, ["table: validation body", "validation body", "body"])
                            if value and value != "INFO_NOT_FOUND":
                                cell.text = value
                                print(f"      > Filled: Validation body = {value}")
                                filled = True
                    
                    # SECTORAL SCOPE TABLE (Section 1.3)
                    elif "sectoral scope" in row_label.lower():
                        value = get_value_for_key_pattern(ai_json_data, ["table: sectoral scope", "sectoral scope", "scope"])
                        if value and value != "INFO_NOT_FOUND":
                            cell.text = value
                            print(f"      > Filled: Sectoral scope = {value}")
                            filled = True
                    
                    elif "project activity type" in row_label.lower() and "afolu" not in row_label.lower():
                        value = get_value_for_key_pattern(ai_json_data, ["table: activity type", "activity type", "project type"])
                        if value and value != "INFO_NOT_FOUND":
                            cell.text = value
                            print(f"      > Filled: Project activity type = {value}")
                            filled = True
                    
                    elif "afolu project category" in row_label.lower():
                        cell.text = "INFO_NOT_FOUND"  # This is not an AFOLU project
                        print(f"      > Filled: AFOLU category = INFO_NOT_FOUND")
                        filled = True
                    
                    # Generic fallback - try to match with any available data
                    if not filled:
                        search_terms = []
                        if row_label:
                            search_terms.append(row_label)
                        if col_header:
                            search_terms.append(col_header)
                        
                        if search_terms:
                            value = get_value_for_key_pattern(ai_json_data, search_terms)
                            if value and value != "INFO_NOT_FOUND":
                                cell.text = value
                                print(f"      > Filled: {row_label} - {col_header} = {value}")
                                filled = True
                    
                    # Ensure no cell is left empty
                    if not filled:
                        cell.text = "INFO_NOT_FOUND"
                        print(f"      > Defaulted: {row_label} - {col_header} = INFO_NOT_FOUND")
        
        doc.save(doc_path)
        print(f"  > Saved section '{start_marker}'")

    except Exception as e:
        print(f"  > ERROR: {e}")
        import traceback
        traceback.print_exc()