import json
import re

def retrieve_contents_list(template_text: str) -> str:
    return template_text[template_text.find("Contents"):template_text.find("Appendix")].strip()

def get_pdd_targets(contents_list):
    pdd_targets = []
    section_heading = ""
    for line in contents_list.splitlines():
        if line.strip() and not line.startswith("Contents"):
            if "." not in line.split()[0]:
                section_heading = " ".join(line.split()[1:-1])
            else:
                subheading = " ".join(line.split()[1:-1])
                subheading_idx = line.split()[0]
                page_num = line.split()[-1]
                pdd_targets.append((section_heading, subheading, subheading_idx, page_num))
    return pdd_targets

def find_target_location(target, template_text):
    char_count = 0
    start_location = -1
    search_text = target[1]  # This should be the full section header like "1.1 Summary Description of the Project"
    
    # Extract just the title part (without section number) for template matching
    if len(target) >= 3 and target[2]:  # Has section index like "1.1"
        title_only = target[1].replace(f"{target[2]} ", "").strip()
    else:
        title_only = search_text
    
    # For templates, we need to find the section AFTER the Contents section
    # Look for "Project Details" as a major section header first
    in_contents_section = True
    project_details_found = False
    
    for line in template_text.splitlines():
        line_clean = line.strip()
        
        # Check if we've moved past the Contents section
        if line_clean == "Project Details" and not project_details_found:
            project_details_found = True
            in_contents_section = False
        
        # Only look for matches after we're past Contents
        if not in_contents_section:
            # Try exact match first
            if line_clean == search_text:
                start_location = char_count
                break
            # Try matching with tabs replaced by spaces
            elif line_clean.replace('\t', ' ') == search_text:
                start_location = char_count 
                break
            # Try matching just the title part (for template sections)
            elif line_clean == title_only:
                start_location = char_count
                break
            # Try partial matching - look for the section number and title parts
            elif search_text in line_clean.replace('\t', ' '):
                start_location = char_count
                break
        
        char_count += len(line) + 1
    
    if start_location == -1: 
        # Fallback: find the last occurrence of the search pattern
        # (to skip Contents and get actual content)
        if title_only in template_text:
            all_positions = []
            search_pos = 0
            while True:
                pos = template_text.find(title_only, search_pos)
                if pos == -1:
                    break
                all_positions.append(pos)
                search_pos = pos + 1
            
            # Use the last occurrence (likely the actual content section)
            if all_positions:
                start_location = all_positions[-1]
    
    return start_location

def assemble_user_prompt(infilling_info):
    """Create a clear prompt for the AI."""
    # Check what type of content this section has
    has_bullets = '•' in infilling_info or '·' in infilling_info
    has_checkboxes = '☐' in infilling_info or '□' in infilling_info
    has_tables = '|' in infilling_info
    
    prompt = f"""
Fill in this document template section using information from the provided context files.

SECTION TO FILL:
---
{infilling_info}
---

INSTRUCTIONS:
"""
    
    if has_bullets:
        prompt += """
- For the bullet points: Provide a separate response for EACH bullet point
- Each bullet should be filled with specific, relevant information
"""
    
    if has_checkboxes:
        prompt += """
- For checkboxes: Specify which ONE option should be selected (e.g., "Single location or installation")
"""
    
    if has_tables:
        prompt += """
- For tables: Fill EVERY empty cell. Use "INFO_NOT_FOUND" if data is not available
"""
    
    prompt += """
- For paragraphs requesting descriptions/explanations: Provide complete, detailed content as "Paragraph: [topic]"
- Example: "Paragraph: General eligibility": {"value": "The project meets all eligibility requirements...", "source": "doc.pdf"}

Return your response as a flat JSON object."""
    
    return prompt

def assemble_system_prompt():
    """System prompt optimized for clarity."""
    return """You must output ONLY valid JSON. No other text.

JSON STRUCTURE:
{
  "key": {"value": "content", "source": "document.pdf"}
}

KEY NAMING RULES:

1. For INDIVIDUAL BULLET POINTS:
"Bullet: technologies": {"value": "60MW solar PV with bifacial modules", "source": "doc.pdf"}
"Bullet: location": {"value": "Kampong Chhnang Province, Cambodia", "source": "doc.pdf"}
"Bullet: GHG reductions": {"value": "Reduces 110,700 tCO2e annually", "source": "doc.pdf"}

2. For CHECKBOXES (specify the option to select):
"Checkbox: Project Design": {"value": "Single location or installation", "source": "doc.pdf"}

3. For TABLE CELLS:
"Table: [RowLabel] - [ColumnHeader]": {"value": "cell content", "source": "doc.pdf"}
Example: "Table: Validation/verification - Period": {"value": "24-March-2021", "source": "doc.pdf"}

4. For PARAGRAPHS requesting descriptions/explanations:
"Paragraph: General eligibility": {"value": "The project meets eligibility requirements by...", "source": "doc.pdf"}
"Paragraph: Project description": {"value": "This project involves...", "source": "doc.pdf"}
"Paragraph: Methodology": {"value": "The methodology used includes...", "source": "doc.pdf"}

5. For missing information:
Always use {"value": "INFO_NOT_FOUND", "source": "N/A"}

IMPORTANT: 
- Fill EVERY bullet point separately
- Fill EVERY table cell
- Keep responses concise but complete"""

def parse_ai_json_response(response_text):
    """Parse AI response robustly."""
    try:
        # Clean up the response
        response_cleaned = response_text.strip()
        
        # Remove markdown formatting
        if "```json" in response_cleaned:
            start = response_cleaned.find("{")
            end = response_cleaned.rfind("}") + 1
            if start >= 0 and end > start:
                response_cleaned = response_cleaned[start:end]
        elif "```" in response_cleaned:
            response_cleaned = response_cleaned.replace("```", "")
        
        # Parse the JSON
        return json.loads(response_cleaned)
        
    except json.JSONDecodeError as e:
        print(f"  > JSON Parse Error: {str(e)[:100]}")
        
        # Try to fix truncated JSON
        try:
            # Count braces
            open_braces = response_cleaned.count('{')
            close_braces = response_cleaned.count('}')
            
            if open_braces > close_braces:
                # Add missing closing braces
                response_cleaned += '}' * (open_braces - close_braces)
                return json.loads(response_cleaned)
        except:
            pass
        
        # Last resort - extract valid entries
        try:
            result = {}
            # Pattern to match complete key-value pairs
            pattern = r'"([^"]+)":\s*\{\s*"value":\s*"([^"]*)"[^}]*\}'
            matches = re.findall(pattern, response_text, re.DOTALL)
            
            for key, value in matches:
                result[key] = {"value": value, "source": "extracted"}
            
            if result:
                print(f"  > Recovered {len(result)} fields from malformed JSON")
                return result
        except:
            pass
        
        return None