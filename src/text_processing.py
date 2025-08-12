

def retrieve_contents_list(template_text: str) -> str:
    return template_text[template_text.find("Contents"):template_text.find("Appendix")].strip()


def get_pdd_targets(contents_list):

    pdd_targets = []
    section_heading = ""
    for line in contents_list.splitlines():
        if "." not in line.split()[0]:
            section_heading = " ".join(line.split()[1:-1])
        else:
            subheading = " ".join(line.split()[1:-1])
            subheading_idx = line.split()[0]
            page_num = line.split()[-1]
            # section heading, subheading title, subheading idx, page num
            pdd_targets.append((section_heading, subheading, subheading_idx, page_num))
    return pdd_targets


def structure_response(target_info): # To require the LLM to output info in a certain format. target_info should contain a field saying whether there are any tables to fill in etc.
    pass






