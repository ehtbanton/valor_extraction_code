

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

            pdd_targets = add_subheading_info(pdd_targets)
    return pdd_targets


def add_subheading_info(pdd_targets):
    for i in range(len(pdd_targets)):
        print(f"\nHeading: {pdd_targets[i][0]} \nSubheading Title: {pdd_targets[i][1]} \nSubheading Index: {pdd_targets[i][2]} \nPage Number: {pdd_targets[i][3]}")
        if i != len(pdd_targets) - 1:
            
    return relevant_info

