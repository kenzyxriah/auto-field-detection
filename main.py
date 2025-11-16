# python -m visuals.main
from visuals.util import *
from process import *


async def visualize(path: str):
    
    data = await get_controls(path)
    
   
    for i, candidates in enumerate(data):
        
        page_width = candidates['pageDimension']['width']
        page_height = candidates['pageDimension']['height']
        visualize_pil2(candidates['controls'], path, i, page_width, page_height)
        


if __name__ == '__main__':
    import asyncio
    PATH = r'C:\Users\Admin\Downloads\Clearance Slip.pdf'
    # PATH = r'C:\Users\Admin\Downloads\SAMPLE Document unsigned.pdf'
    # PATH = r'C:\Users\Admin\Downloads\document.pdf'
    # PATH = r'C:\Users\Admin\Downloads\Reimbursement template.pdf'
    # PATH = r'C:\Users\Admin\Downloads\Health Insurance Agreement - Abdulbasit 1.pdf'
    # PATH = r'C:\Users\Admin\Downloads\FLEXIBLE WORK AGREEMENT- Abdulqahhar Okenla.pdf'
    # PATH = r'C:\Users\Admin\Downloads\Signed_Flowmono-Provisional Offer of Internship - AbdulQahhar Abimbola Okenla.pdf' 
    # PATH = r'C:\Users\Admin\Downloads\ppa_Letter (1).pdf'
    # PATH = r'C:\Users\Admin\Downloads\AbdulQahhar_Employment_Offer_ML_AI_Developer_Babskenky_Co_abdulqahhar_abimbola_okenla.pdf'
    # PATH = r'C:\Users\Admin\Downloads\EMPLOYEE CONSENT FORM.pdf'
    # PATH = r'C:\Users\Admin\Downloads\App Development Agreement Template.pdf'
    # PATH = r'C:\Users\Admin\Downloads\EMPLOYEE BIO-DATA.pdf'
    # PATH = r'C:\Users\Admin\Downloads\13_Page_Document_with_Name_Signature_Date.pdf'
    # PATH = r'C:\Users\Admin\Downloads\Letter_Controls_60_Pages (6).pdf' 
    # PATH = r'C:\Users\Admin\Downloads\63895_Contract_Agreement.pdf'
    # PATH = r'C:/Users/Admin/Downloads/fw9.pdf'
    # PATH = r'C:\Users\Admin\Downloads\DRIVE.Reminder Service Deployment.pdf' #
    # PATH = r'C:\\Users\\Admin\\Documents\\Flowmono.AIService\\DRIVE.Reminder%20Service%20Deployment.docx-a97b3c2d-62f5-4798-a884-956392c0b75f.pdf' # got this from the payload after uploading a word doc.
    # PATH = r'C:\Users\Admin\Downloads\Guarantor_s Form - Babskenky & Co.docx.pdf' #


    asyncio.run(visualize(PATH))


