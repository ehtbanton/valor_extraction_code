#!/usr/bin/env python3
"""Test boundary detection specifically for section 1.4 and its subsections"""

import sys
sys.path.append('src')

from word_editor import load_word_doc_to_string, _iter_block_items, get_heading_level
import docx
import os

def test_section_1_4_boundary():
    print("=== SECTION 1.4 BOUNDARY DETECTION TEST ===")
    
    # Use the actual document
    doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if not os.path.exists(doc_path):
        print(f"Document not found at {doc_path}")
        return
    
    doc = docx.Document(doc_path)
    all_blocks = list(_iter_block_items(doc))
    
    start_marker = "Project Eligibility"
    end_marker = "Project Design"
    
    start_index, end_index = -1, len(all_blocks)
    start_heading_level = 0
    
    print(f"Looking for start marker: '{start_marker}'")
    print(f"Looking for end marker: '{end_marker}'")
    print(f"Total blocks in document: {len(all_blocks)}")
    
    # Find section boundaries using the same logic as the main function
    for i, block in enumerate(all_blocks):
        if isinstance(block, docx.text.paragraph.Paragraph):
            text = block.text.strip()
            current_heading_level = get_heading_level(block)
            
            # Find start marker
            if (text == start_marker or 
                (len(start_marker.split()) > 1 and start_marker in text and
                 not ('\t' in text and any(char.isdigit() for char in text.split('\t')[-1])))):
                if start_index == -1:
                    start_index = i
                    start_heading_level = current_heading_level
                    print(f"  > Found start at block {i}: '{text}' (Level {start_heading_level})")
                    
            # Find end marker after start is found
            elif start_index != -1:
                if (text == end_marker or 
                    (len(end_marker.split()) > 1 and end_marker in text)):
                    end_index = i
                    print(f"  > Found end marker at block {i}: '{text}' (Level {current_heading_level})")
                    break
                elif (start_heading_level > 0 and current_heading_level > 0 and 
                      current_heading_level <= start_heading_level):
                    end_index = i
                    print(f"  > Found end boundary at block {i}: '{text}' (Level {current_heading_level}) - same or higher level")
                    break
    
    if start_index == -1:
        print("Start marker not found!")
        return
    
    print(f"\nBoundary detection results:")
    print(f"Start index: {start_index}")
    print(f"End index: {end_index}")
    print(f"Start heading level: {start_heading_level}")
    
    # Show all blocks in the detected section
    print(f"\n=== BLOCKS WITHIN DETECTED SECTION ({start_index} to {end_index}) ===")
    
    section_1_4_3_found = False
    
    for i in range(start_index, end_index):
        if i < len(all_blocks):
            block = all_blocks[i]
            if isinstance(block, docx.text.paragraph.Paragraph):
                text = block.text.strip()
                level = get_heading_level(block)
                
                # Check if this looks like section 1.4.3 (Transfer project eligibility)
                if "Transfer project eligibility" in text:
                    section_1_4_3_found = True
                    print(f"  Block {i}: '{text}' (Level {level}) *** SECTION 1.4.3 (TRANSFER) FOUND ***")
                elif text and level > 0:
                    print(f"  Block {i}: '{text}' (Level {level}) [HEADING]")
                elif text:
                    print(f"  Block {i}: '{text[:80]}...' (Level {level}) [CONTENT]")
            elif isinstance(block, docx.table.Table):
                print(f"  Block {i}: [TABLE] (Level 0)")
    
    print(f"\n=== ANALYSIS ===")
    print(f"Section 1.4.3 found within boundary: {'YES' if section_1_4_3_found else 'NO'}")
    
    if not section_1_4_3_found:
        print("\nSearching for 'Transfer project eligibility' in entire document:")
        for i, block in enumerate(all_blocks):
            if isinstance(block, docx.text.paragraph.Paragraph):
                text = block.text.strip()
                if "Transfer project eligibility" in text:
                    level = get_heading_level(block)
                    print(f"  Found Transfer project eligibility at block {i}: '{text}' (Level {level})")
                    if i >= end_index:
                        print(f"    *** This is AFTER the detected boundary (end_index={end_index}) ***")
    
    return section_1_4_3_found

if __name__ == "__main__":
    test_section_1_4_boundary()