#!/usr/bin/env python3
"""Test subsection detection for sections 1.1 to 1.5"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc
import os

def test_subsection_detection():
    print("=== SUBSECTION DETECTION TEST (1.1 to 1.5) ===")
    
    # Ensure we have a clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        import shutil
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Mock AI data
    mock_ai_data = {
        "Paragraph: Summary description": {
            "value": "Test solar project content",
            "source": "test.pdf"
        },
        "Sectoral scope": {
            "value": "Energy (renewable sources)",
            "source": "test.pdf"
        }
    }
    
    # Test sections 1.1 through 1.5
    test_sections = [
        ("1.1 Summary Description of the Project", "1.2 Audit History"),
        ("1.2 Audit History", "1.3 Sectoral Scope and Project Type"),
        ("1.3 Sectoral Scope and Project Type", "1.4 Project Eligibility"),
        ("1.4 Project Eligibility", "1.5 Project Design"),
        ("1.5 Project Design", "1.6 Project Proponent"),
    ]
    
    for i, (start_section, end_section) in enumerate(test_sections, 1):
        print(f"\n{'='*60}")
        print(f"TESTING SECTION 1.{i}: {start_section}")
        print(f"{'='*60}")
        
        try:
            replace_section_in_word_doc(
                test_doc_path,
                start_section,
                end_section,
                mock_ai_data,
                "SECTION_COMPLETE"
            )
            print(f"SUCCESS: Section 1.{i} processed")
            
        except Exception as e:
            print(f"ERROR in section 1.{i}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_subsection_detection()