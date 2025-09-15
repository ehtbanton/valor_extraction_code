#!/usr/bin/env python3
"""Debug what's happening in section processing"""

import sys
sys.path.append('src')

from word_editor import load_word_doc_to_string, _iter_block_items, get_heading_level, replace_section_in_word_doc
import docx
import os
import shutil

def debug_section_processing():
    print("=== DEBUGGING SECTION PROCESSING ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Examine Project Eligibility section in template
    doc = docx.Document(test_doc_path)
    all_blocks = list(_iter_block_items(doc))
    
    # Find Project Eligibility section
    start_index = -1
    end_index = -1
    
    for i, block in enumerate(all_blocks):
        if isinstance(block, docx.text.paragraph.Paragraph):
            text = block.text.strip()
            level = get_heading_level(block)
            
            if "Project Eligibility" in text and level == 2:
                start_index = i
                print(f"Found Project Eligibility at block {i}: '{text}'")
            elif start_index != -1 and "Project Design" in text and level == 2:
                end_index = i
                print(f"Found Project Design at block {i}: '{text}'")
                break
    
    if start_index != -1 and end_index != -1:
        print(f"\nProject Eligibility section spans blocks {start_index} to {end_index}")
        print("Content blocks:")
        
        for i in range(start_index, end_index):
            block = all_blocks[i]
            if isinstance(block, docx.text.paragraph.Paragraph):
                text = block.text.strip()
                level = get_heading_level(block)
                
                if text:
                    block_type = "HEADING" if level > 0 else "CONTENT"
                    print(f"  Block {i}: Level {level} [{block_type}] '{text[:80]}...'")
        
        # Test with minimal AI data
        test_ai_data = {
            "General eligibility: Include any other relevant eligibility information": {
                "value": "TEST CONTENT for general eligibility section",
                "source": "test.pdf"
            }
        }
        
        print(f"\nProcessing with minimal AI data...")
        
        # Process section
        replace_section_in_word_doc(
            test_doc_path,
            "Project Eligibility",
            "Project Design", 
            test_ai_data,
            "SECTION_COMPLETE"
        )
        
        # Check result
        print(f"\nChecking processed result...")
        processed_content = load_word_doc_to_string(test_doc_path)
        
        # Find processed section
        start = processed_content.find("Project Eligibility")
        if start != -1:
            end = processed_content.find("Project Design", start + 100)  # Skip TOC entry
            if end != -1:
                processed_section = processed_content[start:end]
                print(f"Processed section length: {len(processed_section)} characters")
                
                # Check if our test content is there
                if "TEST CONTENT for general eligibility" in processed_section:
                    print("✓ Test content found in processed section")
                else:
                    print("✗ Test content NOT found in processed section")
                
                # Show structure
                lines = processed_section.split('\n')[:15]
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"  Line {i+1}: {line.strip()[:100]}")
            else:
                print("Could not find end of processed section")
        else:
            print("Could not find processed section")
    
    else:
        print("Could not locate Project Eligibility section boundaries")

if __name__ == "__main__":
    debug_section_processing()