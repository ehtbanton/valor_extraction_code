#!/usr/bin/env python3
"""Test hierarchical content processing with nested sections"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string
import os

def test_hierarchical_processing():
    print("=== HIERARCHICAL CONTENT PROCESSING TEST ===")
    
    # Ensure we have a clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        import shutil
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    else:
        print(f"WARNING: Template not found at {template_source}")
        
    # Rich AI data for testing hierarchical matching
    hierarchical_ai_data = {
        # Main section content
        "Paragraph: Summary description of technologies/measures": {
            "value": "The project involves developing a 60MW solar photovoltaic power plant using bifacial modules and single-axis tracking systems to maximize energy generation efficiency.",
            "source": "project_design_doc.pdf"
        },
        
        # Subsection-specific content
        "Paragraph: Location of the project": {
            "value": "The solar facility is located in Kampong Chhnang Province, Cambodia, covering approximately 120 hectares of agricultural land with optimal solar irradiation conditions.",
            "source": "site_assessment.pdf"
        },
        
        # Table content that should work regardless of hierarchy
        "Sectoral scope": {
            "value": "Energy (renewable/non-renewable sources)",
            "source": "vcs_methodology.pdf"
        },
        
        "Project activity type": {
            "value": "Renewable energy generation - Solar photovoltaic",
            "source": "project_definition.pdf"
        },
        
        # Various content patterns for testing matching
        "project description": "Advanced solar PV technology implementation",
        "technical details": "Bifacial solar panels with tracking systems",
        "location information": "Rural agricultural area in Cambodia",
        "environmental impact": "Minimal environmental disruption with land restoration",
        
        # Audit history table content (multi-column)
        "Validation Name of auditor": {
            "value": "TUV NORD Cert GmbH",
            "source": "audit_records.pdf"
        },
        
        "Validation Date completed": {
            "value": "2024-03-15",
            "source": "audit_records.pdf"
        }
    }
    
    # Test sections that are known to have hierarchical content
    test_sections = [
        # Should work with existing functionality
        ("1.3 Sectoral Scope and Project Type", "1.4 Project Eligibility"),
        
        # Should now work with hierarchical processing
        ("1.1 Summary Description of the Project", "1.2 Audit History"),
        
        # Another hierarchical section
        ("2.1 Stakeholder Engagement and Consultation", "2.2 Risks to Stakeholders and the Environment"),
    ]
    
    results = []
    
    for start_section, end_section in test_sections:
        print(f"\n{'='*60}")
        print(f"TESTING HIERARCHICAL SECTION: {start_section}")
        print(f"{'='*60}")
        
        try:
            # Process the section
            replace_section_in_word_doc(
                test_doc_path,
                start_section,
                end_section,
                hierarchical_ai_data,
                "SECTION_COMPLETE"
            )
            
            results.append({
                'section': start_section,
                'status': 'SUCCESS',
                'error': None
            })
            print(f"SUCCESS: {start_section} processed without errors")
            
        except Exception as e:
            results.append({
                'section': start_section,
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"FAILED: {start_section} - Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Verify document integrity
    print(f"\n{'='*60}")
    print("DOCUMENT INTEGRITY CHECK")
    print(f"{'='*60}")
    
    try:
        doc_content = load_word_doc_to_string(test_doc_path)
        
        # Check for common issues
        issues = []
        
        if "FATAL ERROR" in doc_content:
            issues.append("Fatal errors found in document")
        
        # Check if content was actually added
        content_indicators = [
            "solar photovoltaic", 
            "bifacial modules", 
            "Kampong Chhnang",
            "TUV NORD"
        ]
        
        added_content_count = sum(1 for indicator in content_indicators if indicator.lower() in doc_content.lower())
        
        print(f"Content indicators found: {added_content_count}/{len(content_indicators)}")
        
        if added_content_count == 0:
            issues.append("No AI-generated content detected in document")
        
        # Check for document corruption
        corruption_patterns = ['[ ] 1.', '[X] 1.', '[ ] Section']
        corruption_found = any(pattern in doc_content for pattern in corruption_patterns)
        
        if corruption_found:
            issues.append("Document corruption detected (checkboxes in headings)")
        
        if issues:
            print("ISSUES DETECTED:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Document integrity: GOOD")
            
    except Exception as e:
        print(f"Document integrity check failed: {e}")
        issues = ["Document integrity check failed"]
    
    # Final summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    print(f"Sections tested: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    for result in results:
        status_symbol = "✓" if result['status'] == 'SUCCESS' else "✗"
        print(f"  {status_symbol} {result['section']}")
        if result['error']:
            print(f"    Error: {result['error']}")
    
    overall_success = success_count == total_count and not issues
    print(f"\nOVERALL RESULT: {'SUCCESS' if overall_success else 'ISSUES DETECTED'}")
    
    return overall_success

if __name__ == "__main__":
    test_hierarchical_processing()