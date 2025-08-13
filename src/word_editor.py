import docx
import os



def get_infilling_info(target, pdd_targets,):
    template_path = get_template_path()
    if not template_path:
        raise FileNotFoundError("No .docx template found in the 'output_template' folder.")
    
    doc=docx.Document(template_path)
    infilling_info = []
    target_subheading = target[1]
    is_target_section = False
    
    current_target_index = pdd_targets.index(target)
    next_target_subheading = None
    if current_target_index + 1 <len(pdd_targets):
        next_target_subheading = pdd_targets[current_target_index + 1][1]

    for i, element in enumerate(doc.element.body):
        if is_target_section:
            if next_target_subheading and isinstance(element,docx.oxml.text.paragraph.CT_P) and docx.text.paragraph.Paragraph(element,doc).text.strip()==next_target_subheading.strip():
                break
            
            if isinstance(element, docx.oxml.text.paragraph.CT_P):
                paragraph = docx.text.paragraph.Paragraph(element, doc)
                if paragraph.text.strip().startswith("[") and paragraph.text.strip().endswith("]"):
                    infilling_type = 'text'
                    infilling_instructions = paragraph.text.strip()
                    infilling_info.append((i, infilling_type, infilling_instructions))

            elif isinstance(element,docx.oxml.table.CT_Tbl):
                table = docx.table.Table(element, doc)
                infilling_type = 'table'
                headers = [cell.text.strip() for cell in table.rows[0].cells]
                infilling_instructions = "A table with the following headers: " + ",".join(headers)
                infilling_info.append((i, infilling_type, infilling_instructions))

        if isinstance(element, docx.oxml.text.paragraph.CT_P):
            paragraph = docx.text.paragraph.Paragraph(element, doc)
            if paragraph.text.strip() == target_subheading.strip():
                is_target_section = True

    return infilling_info

    


#def fill_in_output_doc(target, infilling_info, response):