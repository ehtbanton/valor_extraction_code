

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
    # System prompt contains a static description of how to produce output. An EXACT FORMAT.
    system_prompt = "You are being provided with a template for your response by the user. It contains a list of short descriptions of information you will have to find in the attached documents. Please attempt to locate all relevant information from the attached documents. Ensure your response follows the same format as the user prompt. Specifically, put paragraphs in the same places outlined by the user-provided template, and use the same format as they do for tables. If no relevant information can be found for any part of the template, please write that this is the case in caps at this point in your filled-in template. Ensure your filled-in template format and structure is identical to the template provided by the user. Your response should only contain the filled-in template and no other text."
    return system_prompt

def is_valid_response(response, infilling_info):
    # For now make no checks
    return True

