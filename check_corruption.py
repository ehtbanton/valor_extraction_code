import sys
sys.path.append('src')
from word_editor import load_word_doc_to_string

doc = load_word_doc_to_string('auto_pdd_output')
result = doc.find('[ ] Grouped project design')
if result != -1:
    print('Subheading corruption found!')
    print(doc[result-100:result+200])
else:
    print('No subheading corruption found')
    
# Also check for other potential corruption patterns
patterns = ['[ ] 1.', '[ ] 2.', '[ ] 3.', '[X] 1.', '[X] 2.']
for pattern in patterns:
    if pattern in doc:
        print(f'Found corrupted pattern: {pattern}')
        pos = doc.find(pattern)
        print(doc[pos-50:pos+100])
        print('---')