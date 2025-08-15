

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

EXHAUSTIVE SEARCH REQUIREMENTS:
- Before marking ANY field as "INFORMATION NOT FOUND", perform THREE separate search passes:
  PASS 1: Search for exact terminology from the template
  PASS 2: Search for synonyms, related terms, and technical variations
  PASS 3: Search for contextual information that could be interpreted as the required data
- Look in ALL document types: technical specs may be in environmental docs, dates may be in funding docs
- Check document titles, headers, footers, and metadata sections
- Look for information in charts, graphs, and table captions
- Search for partial matches that could be combined to create complete answers

EXPANDED SEARCH TERMS:
- Validation → verification, assessment, evaluation, review, approval, certification
- Audit → monitoring, inspection, compliance check, oversight, review
- Timeline → schedule, phases, milestones, implementation period, duration
- Capacity → power rating, output, generation capacity, installed capacity
- Location → site, coordinates, address, geographic position, project area

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
- Do not leave entire rows empty; fill each row's cells individually.
- Replace pre-filled example text entirely.
- Maintain original column headers exactly as provided.
- Do not add extra rows or columns.

EDGE CASE HANDLING:
- For partial information: include what you find; if incomplete, retain partial data exactly as found.
- For conflicting information: use the most technically detailed or most recent source; if multiple dates or values are plausible, report the full range.
- For ranges or estimates: include the full range (e.g., "60-80 MW" not just "60 MW").
- For dates: use exact dates when available; retain partial dates (month/year) if precise day is not provided.
- If a table has no data in any row, still output the table with all cells as "INFORMATION NOT FOUND".

OUTPUT CONSTRAINTS:
- Start directly with the template content and end when the template content ends.
- Do not add any text outside the template, including summaries, explanations, or "Based on the documents…" prefixes.
- Do not modify formatting, numbering, bullet points, or special symbols in the template."""
    
    return system_prompt


def is_valid_response(response, infilling_info):
    # For now make no checks
    return True

def create_followup_prompt(response, infilling_info):
    """Create a targeted follow-up prompt for missing information"""
    
    missing_fields = []
    for line in response.split('\n'):
        if "INFORMATION NOT FOUND" in line:
            # Extract context around the missing field
            missing_fields.append(line.strip())
    
    if not missing_fields:
        return None
    
    followup_prompt = f"""The following specific information was marked as "INFORMATION NOT FOUND" in a previous analysis:

{chr(10).join(missing_fields)}

Please perform a comprehensive re-search of ALL uploaded documents specifically for this missing information. Look for:
- Alternative terminology and synonyms
- Information that might be embedded in longer paragraphs
- Data in unexpected document sections (e.g., technical specs in environmental docs)
- Partial information that could be pieced together
- Information in document metadata, headers, or appendices

For each missing item, provide either:
1. The specific information found (with source context)
2. Confirmation that it truly does not exist in any document

Format your response as:
FIELD: [found information OR "CONFIRMED NOT FOUND"]
"""
    
    return followup_prompt

def count_missing_fields(response):
    """Count how many fields are marked as INFORMATION NOT FOUND"""
    return response.count("INFORMATION NOT FOUND")

def merge_followup_response(original_response, followup_response):
    """Merge follow-up findings back into original response"""
    lines = original_response.split('\n')
    
    # Parse followup response for found information
    followup_findings = {}
    for line in followup_response.split('\n'):
        if ':' in line and ('FIELD:' in line or any(keyword in line.upper() for keyword in ['VALIDATION', 'AUDIT', 'PERIOD', 'BODY', 'YEARS'])):
            parts = line.split(':', 1)
            if len(parts) == 2:
                field_context = parts[0].strip()
                found_info = parts[1].strip()
                if found_info != "CONFIRMED NOT FOUND" and "NOT FOUND" not in found_info:
                    followup_findings[field_context] = found_info
    
    # Replace INFORMATION NOT FOUND with found information
    updated_lines = []
    for line in lines:
        if "INFORMATION NOT FOUND" in line and followup_findings:
            # Try to match this line with followup findings
            line_updated = False
            for field_context, found_info in followup_findings.items():
                # Simple matching - could be made more sophisticated
                if any(word in line.upper() for word in field_context.upper().split()):
                    updated_lines.append(line.replace("INFORMATION NOT FOUND", found_info))
                    line_updated = True
                    break
            if not line_updated:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    return '\n'.join(updated_lines)

