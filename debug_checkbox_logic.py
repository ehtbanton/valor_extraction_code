#!/usr/bin/env python3
"""Debug the checkbox logic specifically"""

# Test what happens with the actual block text
block_text = "  Single location or installation"
value = "No"

# Current logic
original_text = block_text.replace('☐', '').replace('[ ]', '').replace('[X]', '').strip()
print(f"Original block text: {repr(block_text)}")
print(f"AI value: {repr(value)}")
print(f"After cleanup: {repr(original_text)}")

if value.lower() in ['no', 'n', 'false', '0']:
    result = f"☐ {original_text}"
    print(f"Final result: {repr(result)}")

# Test with Yes
value = "Yes"
if value.lower() in ['yes', 'y', 'true', '1']:
    result = f"☒ {original_text}"
    print(f"Final result for Yes: {repr(result)}")