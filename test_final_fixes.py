#!/usr/bin/env python3
"""Test all fixes together with actual data format"""

import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc, load_word_doc_to_string
import os
import shutil

def test_all_fixes():
    print("=== TESTING ALL FIXES WITH ACTUAL DATA FORMAT ===")
    
    # Use clean template
    template_source = "output_template/VCS-Project-Description-Template-v4.4-FINAL2.docx"
    test_doc_path = "auto_pdd_output/AutoPDD_prime_road.docx"
    
    if os.path.exists(template_source):
        shutil.copy(template_source, test_doc_path)
        print(f"Copied clean template to: {test_doc_path}")
    
    # Use actual AI data format from your terminal output
    eligibility_data = {
        "General eligibility: Justify that the project activity is included under the scope of the VCS Program and not excluded under Table 2.1 of the VCS Standard.": {
            "value": "The project is a 60 MWac utility-scale solar photovoltaic (PV) power project that contributes to ADB's climate change mitigation efforts by reducing annual greenhouse gas emissions by 110,700 tons per year and aligns with Cambodia's Nationally Determined Contribution (NDC) to reduce GHG emissions. No explicit information is found linking the project activity to the specific scope of the VCS Program or exclusion criteria under Table 2.1 of the VCS Standard.",
            "source": "Prime Road FUNDING PROPOSAL.pdf, Prime Road ENVIRONMENTAL IMPACT.pdf"
        },
        "General eligibility: Demonstrate that the applied methodology is eligible under the VCS Program. Where applying a methodology with scale and/or capacity limits, demonstrate that the project is not a fragmented part of a larger project or activity that would otherwise exceed such limits. If applicable, demonstrate that no single cluster of project activity instances exceeds the capacity limit.": {
            "value": "The project represents phase 1 of the planned 100 MWac Cambodian National Solar Park Project, with the remaining 40 MWac capacity to be tendered in a second phase. The first phase is a 60 MWac solar power plant. No information is available regarding the applied methodology's eligibility under the VCS Program or specific scale/capacity limits that would determine if this phased approach constitutes a fragmented part exceeding such limits.",
            "source": "Prime Road FUNDING PROPOSAL.pdf, Prime Road ENVIRONMENTAL IMPACT.pdf"
        },
        "General eligibility: Include any other relevant eligibility information.": {
            "value": "The project is a utility-scale solar photovoltaic (PV) power project in Kampong Chhnang Province. It is categorized as Effective Gender Mainstreaming (EGM) and is classified as category B for environment, category C for involuntary resettlement, and category C for indigenous peoples in compliance with ADB's Safeguard Policy Statement (2009).",
            "source": "Prime Road FUNDING PROPOSAL.pdf, Prime Road ENVIRONMENTAL IMPACT.pdf, Prime Road GENDER ACTION PLAN.pdf, Prime Road POVERTY AND SOCIAL ANALYSIS.pdf"
        },
        "AFOLU project eligibility: Justify and demonstrate that all selected AFOLU project categories are appropriate and that all related category requirements are met.": {
            "value": "INFO_NOT_FOUND",
            "source": "N/A"
        },
        "Transfer project eligibility: For transfer projects and CPAs seeking registration, justify how eligibility conditions have been met. The response should justify how the criteria in Appendix 2 and Section 3.23 (Double Counting and Participation under Other GHG Programs) of the VCS Standard have been met.": {
            "value": "INFO_NOT_FOUND",
            "source": "N/A"
        }
    }
    
    design_data = {
        "Project Design: Single location or installation": {
            "value": "No",
            "source": "Prime Road FUNDING PROPOSAL.pdf; Prime Road ENVIRONMENTAL IMPACT.pdf"
        },
        "Project Design: Multiple locations or project activity instances (but not a grouped project)": {
            "value": "Yes",
            "source": "Prime Road FUNDING PROPOSAL.pdf (page 1, paragraph 10); Prime Road ENVIRONMENTAL IMPACT.pdf (Executive Summary, paragraph 1)"
        },
        "Project Design: Grouped project": {
            "value": "No",
            "source": "Prime Road FUNDING PROPOSAL.pdf; Prime Road ENVIRONMENTAL IMPACT.pdf"
        }
    }
    
    print("\n--- Testing Project Eligibility Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Eligibility",
            "Project Design", 
            eligibility_data,
            "SECTION_ATTEMPTED"  # Using SECTION_ATTEMPTED since some values are INFO_NOT_FOUND
        )
        print("✓ Project Eligibility processed successfully")
        
    except Exception as e:
        print(f"✗ Project Eligibility failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n--- Testing Project Design Section ---")
    try:
        replace_section_in_word_doc(
            test_doc_path,
            "Project Design",
            "Project Proponent", 
            design_data,
            "SECTION_COMPLETE"
        )
        print("✓ Project Design processed successfully")
        
    except Exception as e:
        print(f"✗ Project Design failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final verification
    print("\n--- Final Verification ---")
    doc_content = load_word_doc_to_string(test_doc_path)
    
    # Check Project Eligibility content
    eligibility_indicators = [
        "60 MWac utility-scale solar photovoltaic",
        "phase 1 of the planned 100 MWac",
        "category B for environment"
    ]
    
    eligibility_found = 0
    for indicator in eligibility_indicators:
        if indicator in doc_content:
            eligibility_found += 1
    
    print(f"Project Eligibility content found: {eligibility_found}/{len(eligibility_indicators)}")
    
    # Check subsection headings are preserved
    subsection_headings = ["General eligibility", "AFOLU project eligibility", "Transfer project eligibility"]
    headings_preserved = 0
    for heading in subsection_headings:
        if heading in doc_content:
            headings_preserved += 1
    
    print(f"Subsection headings preserved: {headings_preserved}/{len(subsection_headings)}")
    
    # Check checkbox processing
    checkbox_count = doc_content.count('\u2610') + doc_content.count('\u2612')  # ☐ + ☒
    yes_no_count = doc_content.count('No\n\nYes\n\nNo')  # Bad formatting
    
    print(f"Checkbox symbols found: {checkbox_count}")
    print(f"Bad Yes/No formatting: {'YES' if yes_no_count > 0 else 'NO'}")
    
    # Overall assessment
    success = (eligibility_found >= 2 and headings_preserved >= 2 and checkbox_count >= 1 and yes_no_count == 0)
    print(f"\nOVERALL RESULT: {'SUCCESS' if success else 'NEEDS WORK'}")
    
    return success

if __name__ == "__main__":
    test_all_fixes()