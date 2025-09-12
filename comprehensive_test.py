#!/usr/bin/env python3
"""Comprehensive test of the document processing system"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string

def comprehensive_test():
    print("=== COMPREHENSIVE DOCUMENT PROCESSING TEST ===")
    
    # Rich mock AI data covering various scenarios
    mock_ai_data = {
        # Paragraph content
        "Paragraph: Summary description of technologies/measures": {
            "value": "The project involves developing a 60MW solar PV power plant with bifacial modules and advanced tracking systems.",
            "source": "test.pdf"
        },
        "Paragraph: Location of the project": {
            "value": "Located in Kampong Chhnang Province, Cambodia, covering approximately 120 hectares.",
            "source": "test.pdf"
        },
        
        # Checkbox options
        "Checkbox: Project Design": {
            "value": "Single location or installation",
            "source": "test.pdf"
        },
        
        # Table content
        "Table: Sectoral scope": {
            "value": "Energy (renewable/non-renewable sources)",
            "source": "test.pdf"
        },
        "Table: Project activity type": {
            "value": "Renewable energy generation - solar",
            "source": "test.pdf"
        },
        
        # Various patterns
        "single location": "Single location or installation",
        "describe project": "Solar photovoltaic power generation facility",
        "provide summary": "Renewable energy project using solar PV technology",
    }
    
    # Test multiple sections
    sections_to_test = [
        ("1.1 Summary Description of the Project", "1.2 Audit History"),
        ("1.3 Sectoral Scope and Project Type", "1.4 Project Eligibility"),
        ("1.5 Project Design", "1.6 Project Proponent"),
    ]
    
    all_success = True
    
    for start_section, end_section in sections_to_test:
        print(f"\n--- Testing {start_section} ---")
        try:
            replace_section_in_word_doc(
                "auto_pdd_output/AutoPDD_prime_road.docx",
                start_section,
                end_section,
                mock_ai_data,
                "SECTION_COMPLETE"
            )
            print(f"SUCCESS: {start_section}")
            
        except Exception as e:
            print(f"ERROR in {start_section}: {e}")
            import traceback
            traceback.print_exc()
            all_success = False
    
    # Check for corruption patterns
    print("\n--- Checking for corruption patterns ---")
    doc_content = load_word_doc_to_string('auto_pdd_output/AutoPDD_prime_road.docx')
    
    corruption_patterns = [
        ('[ ] Grouped project design', 'checkbox in section title'),
        ('[ ] 1.', 'checkbox in section number'),
        ('[X] 1.', 'selected checkbox in section number'),
        ('[ ] Project Design', 'checkbox in main heading'),
    ]
    
    corruption_found = False
    for pattern, description in corruption_patterns:
        if pattern in doc_content:
            print(f"CORRUPTION FOUND: {description} - '{pattern}'")
            corruption_found = True
    
    if not corruption_found:
        print("No corruption patterns detected")
    
    # Summary
    print(f"\n=== TEST RESULTS ===")
    print(f"Section processing: {'ALL PASSED' if all_success else 'SOME FAILED'}")
    print(f"Corruption check: {'CLEAN' if not corruption_found else 'CORRUPTION FOUND'}")
    print(f"Overall result: {'SUCCESS' if all_success and not corruption_found else 'ISSUES DETECTED'}")
    
    return all_success and not corruption_found

if __name__ == "__main__":
    comprehensive_test()