#!/usr/bin/env python3
"""Test the actual content processing for Project Eligibility section"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string
import os
import shutil

def test_project_eligibility_content_processing():
    print("=== PROJECT ELIGIBILITY CONTENT PROCESSING TEST ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    else:
        print(f"Template not found at {template_source}")
        return
    
    # Create realistic AI data that should match content in all three subsections
    mock_ai_data = {
        # General eligibility content (1.4.1)
        "General eligibility - For all projects": {
            "value": "This is test content for general eligibility section",
            "source": "test.pdf"
        },
        "General eligibility": {
            "value": "General eligibility test content",
            "source": "test.pdf"
        },
        "For all projects, describe and justify": {
            "value": "Justified general eligibility content",
            "source": "test.pdf"
        },
        
        # AFOLU project eligibility content (1.4.2)
        "AFOLU project eligibility": {
            "value": "This project is not AFOLU related - it is a solar energy project",
            "source": "test.pdf"
        },
        "AFOLU project": {
            "value": "Solar project, not AFOLU",
            "source": "test.pdf"
        },
        
        # Transfer project eligibility content (1.4.3)
        "Transfer project eligibility": {
            "value": "This is TEST CONTENT for transfer project eligibility - Section 1.4.3",
            "source": "test.pdf"
        },
        "Transfer project": {
            "value": "Transfer eligibility test content",
            "source": "test.pdf"
        },
        "For transfer projects and CPAs": {
            "value": "Transfer project justification content",
            "source": "test.pdf"
        },
        
        # Additional patterns that might match
        "project eligibility": "General project eligibility content",
        "transfer eligibility": "Transfer-specific content",
        "eligibility conditions": "Eligibility conditions content"
    }
    
    print(f"Mock AI data contains {len(mock_ai_data)} keys")
    
    # Process the Project Eligibility section
    print("\n--- Processing Project Eligibility Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Eligibility",
            "Project Design", 
            mock_ai_data,
            "SECTION_COMPLETE"
        )
        print("Section processing completed without errors")
        
    except Exception as e:
        print(f"ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check the result
    print("\n--- Checking processed content ---")
    try:
        doc_content = load_word_doc_to_string(test_doc_path)
        
        # Look for our test content in the document
        test_patterns = [
            ("General eligibility test content", "1.4.1 General eligibility"),
            ("Solar project, not AFOLU", "1.4.2 AFOLU eligibility"),
            ("TEST CONTENT for transfer project eligibility", "1.4.3 Transfer eligibility")
        ]
        
        results = {}
        for pattern, section_name in test_patterns:
            found = pattern in doc_content
            results[section_name] = found
            print(f"{section_name}: {'FILLED' if found else 'NOT FILLED'}")
            if found:
                # Find the context around the match
                index = doc_content.find(pattern)
                start = max(0, index - 100)
                end = min(len(doc_content), index + len(pattern) + 100)
                context = doc_content[start:end].replace('\n', ' ')
                print(f"  Context: ...{context}...")
        
        # Special focus on 1.4.3
        if not results.get("1.4.3 Transfer eligibility", False):
            print(f"\n*** SECTION 1.4.3 NOT FILLED - Searching for Transfer content ***")
            
            if "Transfer project eligibility" in doc_content:
                print("Found 'Transfer project eligibility' heading in document")
                # Find context around it
                index = doc_content.find("Transfer project eligibility")
                start = max(0, index - 50)
                end = min(len(doc_content), index + 200)
                context = doc_content[start:end].replace('\n', ' ')
                print(f"Context around Transfer heading: ...{context}...")
            else:
                print("'Transfer project eligibility' heading NOT FOUND in document")
        
        return all(results.values())
        
    except Exception as e:
        print(f"ERROR checking content: {e}")
        return False

if __name__ == "__main__":
    success = test_project_eligibility_content_processing()
    print(f"\nOVERALL RESULT: {'SUCCESS - All sections filled' if success else 'FAILURE - Some sections not filled'}")