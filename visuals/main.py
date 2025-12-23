# python -m module.esign.auto_assign.visuals.main
from .util import *
from auto_assign.process import *

async def for_esign_agent(path: str):
    
    data = await get_controls(path)
   
    all_items = []
    for page in data:
        for element in page.get('controls', []):
            
            all_items.append({"name": element['type'],
                "x": element['bbox'][1],
                "y": element['bbox'][0],
                "width": element['bbox'][3] - element['bbox'][1],
                "height": element['bbox'][2] - element['bbox'][0],
                "pageNumber": element["pageNumber"]
                })

    return all_items


async def visualize(path: str):
    
    data = await get_controls(path)
    
    for i, candidates in enumerate(data):
        
        page_width = candidates['pageDimension']['width']
        page_height = candidates['pageDimension']['height']
        visualize_pil2(candidates['controls'], path, i, page_width, page_height)
        


if __name__ == '__main__':
    import asyncio
    # PATH = r'C:\Users\Admin\Downloads\Clearance Slip.pdf'
    # PATH = r'C:\Users\Admin\Downloads\SAMPLE Document unsigned.pdf'
    # PATH = r'C:\Users\Admin\Downloads\App Development Agreement Template.pdf'

    # asyncio.run(visualize(PATH))
    


