import sys
sys.path.append('src')

from word_editor import replace_section_in_word_doc

# Mock AI data for Project Design section - add more specific patterns
mock_data = {
    "Checkbox: Project Design": {"value": "Single location or installation", "source": "test.pdf"},
    "Single location": {"value": "Single location or installation", "source": "test.pdf"},
    "single": "Single location or installation",
    "location": "Single location or installation"
}

# Test section 1.5
try:
    replace_section_in_word_doc(
        "auto_pdd_output/AutoPDD_prime_road.docx",
        "1.5 Project Design", 
        "1.6 Project Proponent",
        mock_data,
        "SECTION_COMPLETE"
    )
    print("SUCCESS: Section 1.5 completed")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()