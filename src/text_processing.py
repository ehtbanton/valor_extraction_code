

def retrieve_contents_list(template_text: str) -> str:
    return template_text[template_text.find("Contents"):template_text.find("Appendix")].strip()


def get_pdd_targets(contents_list):

    pdd_targets = []
    section_heading = ""
    for line in contents_list.splitlines():
        if line.strip() and not line.startswith("Contents"):
            #print(line)
            if "." not in line.split()[0]:
                section_heading = " ".join(line.split()[1:-1])
            else:
                subheading = " ".join(line.split()[1:-1])
                subheading_idx = line.split()[0]
                page_num = line.split()[-1]
                # section heading, subheading title, subheading idx, page num
                pdd_targets.append((section_heading, subheading, subheading_idx, page_num))
    return pdd_targets


def find_target_location(target,template_text):
    char_count = 0
    start_location = -1
    for line in template_text.splitlines():
        if line.strip() == target[1]:  # Found the line containing only target[1]
            start_location = char_count + line.find(target[1])
            break
        char_count += len(line) + 1  # +1 for the newline character
    
    if start_location == -1:
        start_location = template_text.find(target[1])  # Fallback to original method
    return start_location





def assemble_user_prompt(infilling_info):
    # User prompt contains the exact information source from the TEMPLATE.
    user_prompt = infilling_info.strip()
    return user_prompt

def assemble_system_prompt():
    system_prompt = """You are a document analysis assistant filling out a project template with information from provided documents.

CRITICAL INSTRUCTIONS:
1. Follow the EXACT structure and format provided in the user template.
2. Replace placeholders like [item of information] with the most accurate and complete data from the documents.
3. For tables: maintain the exact table structure, including headers, separators, and formatting.
4. If specific information is not found, write "INFORMATION NOT FOUND" in that field. Always use exactly this phrasing.
5. Do NOT write "INFORMATION NOT FOUND" for entire sections; search each cell and row individually.
6. Replace any pre-filled example table rows entirely with extracted data or "INFORMATION NOT FOUND".
7. Your response must contain ONLY the filled template. Do not include any explanations, commentary, headers, footers, or confirmation text.

RELEVANCE CRITERIA:
- Prioritize exact matches for technical specifications, dates, and measurements.
- For descriptive fields, use information that directly addresses the placeholder topic.
- If multiple sources provide the same information, use the most complete version.
- If sources conflict, use the most technically detailed or most recent source.
- Include units of measurement exactly as found in documents; do not convert units unless specified.

TABLE FORMATTING RULES:
- Keep the exact table structure: --- TABLE START --- and --- TABLE END ---.
- Fill each column with relevant information from documents.
- If a cell has no data, write "INFORMATION NOT FOUND".
- Do not leave entire rows empty; fill each row’s cells individually.
- Replace pre-filled example text entirely.
- Maintain original column headers exactly as provided.
- Do not add extra rows or columns.

SEARCH STRATEGY:
- Check all uploaded documents for each piece of required information.
- Look for exact terms first, then synonyms, acronyms, and related technical terms (e.g., validation/verification, audit, crediting period).
- Audit, funding, environmental, and social documents may contain relevant details.
- Timeline information may be scattered; extract the most accurate date range possible.
- For technical specs, prioritize engineering/technical documents over general descriptions.

EDGE CASE HANDLING:
- For partial information: include what you find; if incomplete, retain partial data exactly as found.
- For conflicting information: use the most technically detailed or most recent source; if multiple dates or values are plausible, report the full range.
- For ranges or estimates: include the full range (e.g., "60-80 MW" not just "60 MW").
- For dates: use exact dates when available; retain partial dates (month/year) if precise day is not provided.
- If a table has no data in any row, still output the table with all cells as "INFORMATION NOT FOUND".

OUTPUT CONSTRAINTS:
- Start directly with the template content and end when the template content ends.
- Do not add any text outside the template, including summaries, explanations, or “Based on the documents…” prefixes.
- Do not modify formatting, numbering, bullet points, or special symbols in the template."""
    
    return system_prompt


def is_valid_response(response, infilling_info):
    # For now make no checks
    return True

