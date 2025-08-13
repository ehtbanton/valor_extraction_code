

def retrieve_contents_list(template_text: str) -> str:
    return template_text[template_text.find("Contents"):template_text.find("Appendix")].strip()


def get_pdd_targets(contents_list):

    pdd_targets = []
    section_heading = ""
    for line in contents_list.splitlines():
        if line.strip() and not line.startswith("Contents"):
            print(line)
            if "." not in line.split()[0]:
                section_heading = " ".join(line.split()[1:-1])
            else:
                subheading = " ".join(line.split()[1:-1])
                subheading_idx = line.split()[0]
                page_num = line.split()[-1]
                # section heading, subheading title, subheading idx, page num
                pdd_targets.append((section_heading, subheading, subheading_idx, page_num))
    return pdd_targets


def get_infilling_info(pdd_targets, target_num, template_text):  # Get some array of tuples [(start location, end location, infilling_type, infilling_instructions), ...]
    infilling_info = []
    for idx, target in enumerate(pdd_targets):
        if idx == target_num:
            # Extract relevant information from the template text
            start_location = -1
            char_count = 0
            
            # Search line by line for target[1] as the only content on the line
            for line in template_text.splitlines():
                if line.strip() == target[1]:
                    # Found the line containing only target[1]
                    start_location = char_count + line.find(target[1])
                    break
                char_count += len(line) + 1  # +1 for the newline character
            
            if start_location == -1:
                start_location = template_text.find(target[1])  # Fallback to original method
            
            end_location = start_location + len(target[1])
            infilling_type = "text"  # or "table" based on your logic
            infilling_instructions = "Please provide more details about this section."
            infilling_info.append((start_location, end_location, infilling_type, infilling_instructions))
    return infilling_info



def assemble_user_prompt(target, infilling_info):
    # User prompt contains the exact information source from the TEMPLATE.
    pass


def assemble_system_prompt(infilling_info): # only 
    # System prompt contains a static description of how to produce output. An EXACT FORMAT.
    pass

#def is_valid_response(response, infilling_info):



