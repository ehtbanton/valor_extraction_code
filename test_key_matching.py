#!/usr/bin/env python3
"""Test the improved key matching and checkbox handling"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string
import os
import shutil

def test_improved_key_matching():
    print("=== TESTING IMPROVED KEY MATCHING AND CHECKBOX HANDLING ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Test data matching your actual AI response format
    test_ai_data = {
        # Project Eligibility data - using the format from your actual response
        "General eligibility: Justify that the project activity is included under the scope of the VCS Program and not excluded under Table 2.1 of the VCS Standard": {
            "value": "TEST: This project is eligible under VCS Program and not excluded.",
            "source": "test.pdf"
        },
        "General eligibility: Include any other relevant eligibility information": {
            "value": "TEST: Additional eligibility information provided.",
            "source": "test.pdf"
        },
        "AFOLU project eligibility: For AFOLU projects, describe and justify how the project is eligible to participate in the VCS Program": {
            "value": "TEST: This is not an AFOLU project - it's a solar energy project.",
            "source": "test.pdf"
        },
        "Transfer project eligibility: For transfer projects and CPAs seeking registration, justify how eligibility conditions have been met": {
            "value": "TEST: Transfer eligibility conditions have been met.",
            "source": "test.pdf"
        },
        
        # Project Design checkbox data - using the format from your actual response
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
    
    print(f"Test AI data contains {len(test_ai_data)} keys")
    
    # Test Project Eligibility section
    print("\n--- Testing Project Eligibility Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Eligibility",
            "Project Design", 
            test_ai_data,
            "SECTION_COMPLETE"
        )
        print("Project Eligibility processing completed")
        
    except Exception as e:
        print(f"ERROR in Project Eligibility: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Project Design section
    print("\n--- Testing Project Design Section ---")
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
        print(f"ERROR in Project Design: {e}")
        import traceback
        traceback.print_exc()
    
    # Check results
    print("\n--- Checking Results ---")
    try:
        doc_content = load_word_doc_to_string(test_doc_path)
        
        # Check if Project Eligibility content was filled
        eligibility_indicators = [
            "TEST: This project is eligible under VCS Program",
            "TEST: Additional eligibility information",
            "TEST: This is not an AFOLU project",
            "TEST: Transfer eligibility conditions"
        ]
        
        eligibility_found = 0
        for indicator in eligibility_indicators:
            if indicator in doc_content:
                eligibility_found += 1
                print(f"[FOUND] Eligibility content: {indicator[:50]}...")
            else:
                print(f"[MISSING] Eligibility content: {indicator[:50]}...")
        
        # Check if Project Design checkboxes were handled
        checkbox_indicators = [
            "☒",  # Should have at least one checked box
            "☐"   # Should have unchecked boxes too
        ]
        
        checkbox_found = 0
        for indicator in checkbox_indicators:
            if indicator in doc_content:
                checkbox_found += 1
                print(f"[FOUND] Checkbox symbol: {indicator}")
            else:
                print(f"[MISSING] Checkbox symbol: {indicator}")
        
        print(f"\nSUMMARY:")
        print(f"Project Eligibility content filled: {eligibility_found}/{len(eligibility_indicators)}")
        print(f"Checkbox symbols found: {checkbox_found}/{len(checkbox_indicators)}")
        
        # Look for issues
        if "No" in doc_content and "Yes" in doc_content and "No" in doc_content.split("Project Design")[1][:200]:
            print("[WARNING] Possible checkbox text replacement instead of checkbox formatting")
        
        success = eligibility_found >= 2 and checkbox_found >= 1
        return success
        
    except Exception as e:
        print(f"ERROR checking results: {e}")
        return False

if __name__ == "__main__":
    success = test_improved_key_matching()
    print(f"\nOVERALL TEST RESULT: {'SUCCESS' if success else 'ISSUES DETECTED'}")