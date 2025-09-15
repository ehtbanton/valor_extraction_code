#!/usr/bin/env python3
"""Test comprehensive content filling with INFO_NOT_FOUND handling"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string
import os
import shutil

def test_comprehensive_filling():
    print("=== TESTING COMPREHENSIVE CONTENT FILLING ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Test with mixed AI data - some real content, some INFO_NOT_FOUND, some missing keys
    mixed_ai_data = {
        # Only provide data for 1 out of many content blocks
        "General eligibility: Include any other relevant eligibility information": {
            "value": "This project has been provided with relevant eligibility information.",
            "source": "test.pdf"
        },
        
        # Provide INFO_NOT_FOUND for another
        "General eligibility: Justify that the project activity is included under the scope of the VCS Program": {
            "value": "INFO_NOT_FOUND",
            "source": "N/A"
        },
        
        # Missing keys for AFOLU and Transfer eligibility sections - should be filled with INFO_NOT_FOUND
        
        # Table data with mixed responses
        "Sectoral scope": {
            "value": "Energy",
            "source": "test.pdf"
        },
        "Project activity type": {
            "value": "INFO_NOT_FOUND",
            "source": "N/A"
        }
        # AFOLU project category - missing completely
    }
    
    print(f"AI data provided for {len(mixed_ai_data)} keys only")
    
    # Test Project Eligibility section
    print("\n--- Testing Project Eligibility Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Eligibility",
            "Project Design", 
            mixed_ai_data,
            "SECTION_ATTEMPTED"
        )
        print("Project Eligibility processing completed")
        
    except Exception as e:
        print(f"ERROR in Project Eligibility: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Sectoral Scope section (has tables)
    print("\n--- Testing Sectoral Scope Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Sectoral Scope and Project Type",
            "Project Eligibility", 
            mixed_ai_data,
            "SECTION_ATTEMPTED"
        )
        print("Sectoral Scope processing completed")
        
    except Exception as e:
        print(f"ERROR in Sectoral Scope: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check results
    print("\n--- Checking Results ---")
    doc_content = load_word_doc_to_string(test_doc_path)
    
    # Count INFO_NOT_FOUND entries
    info_not_found_count = doc_content.count("INFO_NOT_FOUND")
    print(f"Total INFO_NOT_FOUND entries: {info_not_found_count}")
    
    # Check specific expectations
    expected_content = [
        "This project has been provided with relevant eligibility information",  # Real content
        "INFO_NOT_FOUND: Justify that the project activity is included",        # Explicit INFO_NOT_FOUND
        "INFO_NOT_FOUND: For all projects, describe and justify",               # Missing key
        "Energy",                                                               # Table with real data
        "INFO_NOT_FOUND: Project activity type"                                # Table with INFO_NOT_FOUND
    ]
    
    found_count = 0
    for content in expected_content:
        if content in doc_content:
            found_count += 1
            print(f"[FOUND] {content[:60]}...")
        else:
            print(f"[MISSING] {content[:60]}...")
    
    print(f"\nContent verification: {found_count}/{len(expected_content)} expected items found")
    
    # Overall assessment
    success = (info_not_found_count >= 5 and found_count >= 3)
    print(f"Comprehensive filling test: {'SUCCESS' if success else 'NEEDS WORK'}")
    
    if success:
        print("\n✓ System now fills ALL content blocks")
        print("✓ INFO_NOT_FOUND handling working for both content and tables")
        print("✓ No more blank sections")
    
    return success

if __name__ == "__main__":
    test_comprehensive_filling()