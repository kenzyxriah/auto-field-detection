from typing import List, Dict
from .filter_ocr import *

confirm_contact = lambda text: any([text.__contains__('phone'),text.__contains__('number'), text.__contains__('contact')])

def get_candidate_fields_per_page(filtered_elements: List[dict], all_coords: Dict, page_key : str, page_width: int| float, is_docx = False) -> List[dict]:

    candidates = []
    all_elements: List[dict] = all_coords[page_key]['elements']
    max_line = max(el.get('line_number') for el in all_elements)
    for label in filtered_elements:
        label_text: str = label.get('text', '').strip()
        label_line = label.get('line_number')
        
            
        if label_text.startswith('[') and label_text.__contains__(']'):
            print('This one is added no questions asked', label)
            candidates.append(label)
            continue # move to the next once met
            
        # get all sorted
        all_sorted = sorted(all_elements, key=lambda el: el['bbox'][0])  
        # Get all elements on the same line
        same_line_elements = [
            el for el in all_elements if el.get('line_number') == label_line
        ]
        same_line_elements = sorted(same_line_elements, key=lambda el: el['bbox'][0])  # Sort by x0

        try:
            label_index = same_line_elements.index(label)
            label_index_for_all = all_sorted.index(label)
        except:
            label_index, label_index_for_all = None, None


        if label_index_for_all is not None:
            
            before_el: dict = all_sorted[label_index_for_all - 1] if label_index_for_all > 0 else None
            previous_el: dict = all_sorted[label_index_for_all - 2] if label_index_for_all > 0 else None
            after_el: dict = same_line_elements[label_index + 1] if label_index + 1 < len(same_line_elements) else None

            before_text: str = before_el.get('text', '').strip() if before_el else ''
            
  

            after_text: str = after_el.get('text', '').strip() if after_el else ''
            
            if after_el:
                after_index = same_line_elements.index(after_el)
                try:
                    next_el = same_line_elements[after_index + 1] if after_index + 1 < len(same_line_elements) else None
                except:
                    next_el = None
                
                try:
                    next_two_el =  same_line_elements[after_index + 2] if after_index + 1 < len(same_line_elements) else None
                except:
                    next_two_el = None
            else: 
                next_el = None
                next_two_el = None
         
            
            
            try:
                if previous_el.get('line_number')  == label_line:
                    conjoined = f"{previous_el.get('text', '').lower()} {before_el.get('text', '').lower()}"
                else:
                    conjoined = ''
                
            except:
                conjoined = ''
        

            if (label_text.__contains__('…') or label_text.__contains__('__') or label_text.__contains__('....')) : # if its a text but a line
                print('this one is a text line', label)
                
                keyss = ['sign', 'date', 'name', 'mail',
                         'phone', 'number', 'contact', 'address']
                conjoined_keys = keyss[2:]
                y = [str(conjoined.lower().__contains__(i)) for i in conjoined_keys]
                z = [str(before_text.lower().__contains__(i)) for i in keyss]

                y_key_idx = y.index('True') if 'True' in y else None
                z_key_idx = z.index('True') if 'True' in z else None
 
                if (before_el.get('line_number') - label.get('line_number') == 1):
                    pass
                
                
                elif z_key_idx is not None:
                    print('before text has item;', before_text)
                    label['text'] = keyss[z_key_idx]
            

                elif y_key_idx is not None:
                    print('Conjoined text has item;', conjoined)
                    label['text'] = conjoined_keys[y_key_idx]
                
                elif max_line - label.get('line_number') <= 2: 
                    label['text'] = 'Signature'
                
                
                candidates.append(label)
                
            elif after_text.__contains__('……') or after_text.__contains__('__') or after_text.__contains__('....'): # skipped as its already checked above 
                continue
            
            #  After element is ':' 
            elif after_text in [':']:
                print('this one has : as after text', label)
                extended_el = after_el.copy()
                if next_el :
                    diff= next_el['bbox'][1] - extended_el['bbox'][3] # range of space between : and the next element
                    if diff >= (0.3 * page_width):
                        extended_el['text'] = label_text
                        extended_el['bbox'][3] = next_el['bbox'][1]
                        candidates.append(extended_el)
                elif not next_el:
                    extended_el['text'] = label_text
                    extended_el['bbox'][3] = page_width - 50
                    candidates.append(extended_el)
                continue
                    

            elif (label_text.__contains__(':') and any(kw in label_text.lower() for kw in KEYWORDS)):
                print('This one contains: ', label)
                threshold = label['bbox'][3]
                label['bbox'][1] = label['bbox'][3] 
                      # i did 50 here, but it was 30 % of page width up why?              
                if after_el and (after_el['bbox'][1] - threshold >= 50) and  label_text.lower().startswith('sign'):
                    label['text'] = 'Signature'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50) and 'date' in label_text.lower():
                    label['text'] = 'Date'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50) and 'name' in label_text.lower():
                    label['text'] = 'Name'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50) and 'mail' in label_text.lower():
                    label['text'] = 'Email'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50) and confirm_contact(label_text.lower()):
                    label['text'] = 'Phone No'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50) and 'address' in label_text.lower():
                    label['text'] = 'Address'
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)
                elif after_el and (after_el['bbox'][1] - threshold >= 50): # dont include labels with close items afterwards
                    label['bbox'][3] = after_el['bbox'][1]
                    candidates.append(label)    
                                        
                elif not after_el:
                    label['bbox'][3] = page_width - 70
                    candidates.append(label)
        

            elif (before_text, after_text) in [('[', ']')]:
                print('random')
                candidates.append(label)
            
                
            # strictly only include those with the next text with ] or next upper as ]
            elif label_text.startswith('[') and after_el and after_el.get('text', '').__contains__(']'):
                print('random')
                label['bbox'][3] = after_el['bbox'][3]
                candidates.append(label)
                
            elif label_text.startswith('[') and next_el and next_el.get('text', '').__contains__(']'):
                print('random')
                label['bbox'][3] = next_el['bbox'][3]
                candidates.append(label)
                
            elif label_text.startswith('[') and next_two_el and next_two_el.get('text', '').__contains__(']'):
                print('random')
                label['bbox'][3] = next_two_el['bbox'][3]
                candidates.append(label)
            
            

                
            # After element is line
            elif after_el and after_el.get('type') == 'line':
                print('These ones are of type line')
                if 'sign' in label_text.lower().strip():
                    after_el['type'] = 'Signature'
                elif 'date' in label_text.lower().strip():
                    after_el['type'] = 'Date'
            
                elif 'name' in label_text.lower().strip():
                    after_el['type'] = 'Name'
                    
                elif 'mail' in label_text.lower().strip():
                    after_el['type'] = 'Email'
                
                elif confirm_contact(label_text.lower().strip()):
                    after_el['type'] = 'Phone No'
                
                elif 'address' in label_text.lower().strip():
                    after_el['type'] = 'Address'
                else:
                    
                    after_el['type'] = 'Signature'
                candidates.append(after_el)


        # dont process if it is a docx file sent from frontend cause there will be duplicate of lines
        if not is_docx:
        
            
            for element in all_elements:
                if element.get('type') == 'line':
                    text: str = label.get('text', '').lower().strip()
                    
                    el_line: str = element.get('line_number', '') 
                    line_length = (element['bbox'][3] - element['bbox'][1])
                    if (el_line == label_line - 1 or el_line == label_line + 1) and text.endswith(':'):
                        continue
                    
                    # Above Line over Text (line type only)
                    elif (el_line == label_line - 1) and (line_length <= (0.6 * page_width)): # (risky)
                        if text.__contains__('sign'):
                            element['type'] = 'Signature'
                            candidates.append(element)
                        elif text.__contains__('date') :
                            element['type'] = 'Date'
                            candidates.append(element)
                        elif text.__contains__('name') :
                            element['type'] = 'Name'
                            candidates.append(element)
                        elif text.__contains__('mail') :
                            element['type'] = 'Email'
                            candidates.append(element)
                        elif confirm_contact(text) :
                            element['type'] = 'Phone No'
                            candidates.append(element)
                        elif text.__contains__('address') :
                            element['type'] = 'Address'
                            candidates.append(element)
                        
                        elif not any([text.__contains__('address'), confirm_contact(text),text.__contains__('mail'),
                                    text.__contains__('name'), text.__contains__('signature'), text.__contains__('date')]):
                            element['type'] = 'Text'
                            
                            candidates.append(element)
                            
                        elif line_length <= (0.45 * page_width):
                            element['type'] = 'Signature'
                            
                            candidates.append(element)
                        # print('Line element is', element)

    return candidates

def get_unique_candidates(candidates: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for cand in candidates:
        key = (tuple(cand.get('bbox', [])), cand.get('text', ''))
        if key not in seen:
            seen.add(key)
            unique.append(cand)
    return unique

