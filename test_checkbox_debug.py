#!/usr/bin/env python3
"""Debug checkbox processing specifically"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string, _iter_block_items, get_heading_level
import docx
import os
import shutil

def test_checkbox_debug():
    print("=== CHECKBOX PROCESSING DEBUG ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Exact AI data format from your actual response
    test_ai_data = {
        "Project Design: Single location or installation": {
            "value": "No",
            "source": "test.pdf"
        },
        "Project Design: Multiple locations or project activity instances (but not a grouped project)": {
            "value": "Yes",
            "source": "test.pdf"
        },
        "Project Design: Grouped project": {
            "value": "No",
            "source": "test.pdf"
        }
    }
    
    # First, let's examine the Project Design section in detail
    print("\n--- EXAMINING PROJECT DESIGN SECTION BEFORE PROCESSING ---")
    doc = docx.Document(test_doc_path)
    all_blocks = list(_iter_block_items(doc))
    
    # Find Project Design section
    start_index = -1
    for i, block in enumerate(all_blocks):
        if isinstance(block, docx.text.paragraph.Paragraph):
            text = block.text.strip()
            if "Project Design" in text and get_heading_level(block) > 0:
                start_index = i
                print(f"Found Project Design section at block {i}: '{text}'")
                break
    
    if start_index != -1:
        # Show next 10 blocks
        for i in range(start_index, min(len(all_blocks), start_index + 10)):
            block = all_blocks[i]
            if isinstance(block, docx.text.paragraph.Paragraph):
                text = block.text.strip()
                level = get_heading_level(block)
                is_checkbox = any(char in text for char in ['☐', '☒', '[ ]', '[X]'])
                print(f"Block {i}: Level {level}, Checkbox: {is_checkbox}, Text: '{text[:80]}...'")
    
    # Now process with our function
    print("\n--- PROCESSING PROJECT DESIGN SECTION ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Design",
            "Project Proponent", 
            test_ai_data,
            "SECTION_COMPLETE"
        )
        print("Project Design processing completed")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check results
    print("\n--- CHECKING RESULTS ---")
    doc_content = load_word_doc_to_string(test_doc_path)
    
    # Look for Project Design section
    design_start = doc_content.find("Project Design")
    if design_start != -1:
        design_end = doc_content.find("Project Proponent", design_start)
        if design_end != -1:
            design_section = doc_content[design_start:design_end]
            
            print(f"Project Design section length: {len(design_section)} characters")
            
            # Check for checkbox symbols
            checkbox_chars = ['\u2610', '\u2612']  # ☐ ☒
            for char in checkbox_chars:
                count = design_section.count(char)
                print(f"Checkbox '{char}' count: {count}")
            
            # Check for Yes/No text (which might indicate checkbox processing failed)
            yes_count = design_section.lower().count('yes')
            no_count = design_section.lower().count('no')
            print(f"'Yes' count: {yes_count}")
            print(f"'No' count: {no_count}")
            
            # Show some content (safely)
            safe_content = design_section[:500].encode('ascii', 'replace').decode('ascii')
            print(f"First 500 chars of section: {repr(safe_content)}")
            
        else:
            print("Could not find end of Project Design section")
    else:
        print("Could not find Project Design section")

if __name__ == "__main__":
    test_checkbox_debug()