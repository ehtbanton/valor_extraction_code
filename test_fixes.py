#!/usr/bin/env python3
"""Test the fixes for the document processing system"""

import os
import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc

def test_fixes():
    print("=== Testing Document Processing Fixes ===")
    
    # Mock AI data similar to the real response
    mock_ai_data = {
        "Paragraph: Summary description of technologies/measures": {
            "value": "The project involves developing a 60MW solar PV power plant with bifacial modules.",
            "source": "test.pdf"
        },
        "Paragraph: Location of the project": {
            "value": "Located in Kampong Chhnang Province, Cambodia.",
            "source": "test.pdf"
        },
        "Checkbox: Project Design": {
            "value": "Single location or installation",
            "source": "test.pdf"
        },
        "Table: Sectoral scope": {
            "value": "Energy",
            "source": "test.pdf"
        },
        "Table: Project activity type": {
            "value": "Renewable energy generation - solar",
            "source": "test.pdf"
        }
    }
    
    try:
        output_path = "auto_pdd_output/AutoPDD_prime_road.docx"
        if os.path.exists(output_path):
            print("Testing section 1.1...")
            replace_section_in_word_doc(
                output_path,
                "1.1 Summary Description of the Project",
                "1.2 Audit History",
                mock_ai_data,
                "SECTION_COMPLETE"
            )
            print("SUCCESS: Section 1.1 processed without errors")
            
            print("\nTesting section 1.5...")
            replace_section_in_word_doc(
                output_path,
                "1.5 Project Design", 
                "1.6 Project Proponent",
                mock_ai_data,
                "SECTION_COMPLETE"
            )
            print("SUCCESS: Section 1.5 processed without errors")
            
        else:
            print("WARN: Output document not found")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("\n=== All Tests Completed ===")
    return True

if __name__ == "__main__":
    test_fixes()