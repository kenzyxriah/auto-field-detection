from src import *

async def process(path: str):
    check_docx = lambda x: 'docx' in x
    is_docx = check_docx(path)
    print('Is it a docx file', is_docx)
    extracted: dict[str, dict[str, any]] = extract_pdf_data(path)
    all_fields = []
    
    for page_key, values in extracted.items():
        page_width, page_height = values['width'], values['height']
        values['elements'] = assign_line_numbers(values)

        
        text_data = [x for x in values['elements'] if x['type'] == 'text']
        
        # filter out text that dont matter
        new_extract = filter_items(text_data)
        
        candidates = get_candidate_fields_per_page(new_extract, extracted, page_key, page_width, is_docx)
        
        unique_candidates = get_unique_candidates(candidates)
      
        all_fields.append({
                    "pageDimension": {'width': page_width, 'height': page_height},
                    
                                'controls': unique_candidates})
    
    return all_fields
    
async def get_controls(path: str):
    
    candidate_fields = await process(path)
    
    type_mapping = {'name': 'Name', 'sign': 'Signature', 'date': 'Date', 
                    'phone': 'Phone No', 'mail': 'Email', 'address': 'Address'}
    for element in candidate_fields:
        controls = element.get('controls', [])
        if controls:
            for control in controls:
                del control['line_number']
                text = control.get('text', '').lower().strip() # this is just for text labels, not line
                matched = False

                for keyword, new_type in type_mapping.items():
                    if keyword in text:
                        control['type'] = new_type
                        matched = True
                        break

                if text and not matched: control['type'] = 'Text'

                if 'text' in control: del control['text']

    return candidate_fields

        