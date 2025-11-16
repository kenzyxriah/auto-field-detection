import unicodedata
from dotenv import load_dotenv
import fitz  # PyMuPDF

load_dotenv()

# --- Set PyMuPDF TESSDATA path ---
fitz.TESSDATA_PREFIX = 'C:\\Program Files\\Tesseract-OCR\\tessdata'


def extract_pdf_data(file_path):
    doc = fitz.open(file_path)
    pages_data = {}

    for page_index, page in enumerate(doc):
        page_width, page_height = page.rect.width, page.rect.height
        elements = []
        vertical_buffer = 14

        # --- OCR TEXT ---
        ocr_textpage = page.get_textpage_ocr()
        ocr_words = page.get_text("words", textpage=ocr_textpage)

        for word_data in ocr_words:
            text, x0, y0, x1, y1 = word_data[4], word_data[0], word_data[1], word_data[2], word_data[3]
            if text.strip() and not unicodedata.category(text[0]).startswith('C'): # extract out unicode characters, could use string.printable but that excludes texts with emoji's
                elements.append({
                    "type": "text",
                    "text": text.strip(),
                    "bbox": [y0, x0, y1, x1],
                    "pageNumber": page_index + 1
                })
                

        # --- DRAWINGS (LINES) ---
        drawings = page.get_drawings()
        for d in drawings:
            for item in d["items"]:
                if item[0] == "l":  # line
                    p1, p2 = item[1], item[2]
                    x0, y0 = p1.x, p1.y
                    x1, y1 = p2.x, p2.y

 
                    if abs(y0 - y1) < 1:  # horizontal line
                        x_min = min(x0, x1)
                        x_max = max(x0, x1)

                        y_min_ext = min(y0, y1) - vertical_buffer
                        y_max_ext = max(y0, y1) 

                        elements.append({
                            "type": "line",
                            "bbox": [y_min_ext, x_min, y_max_ext, x_max],
                            "pageNumber": page_index + 1
                        })

        # --- Sort elements: top-to-bottom, then left-to-right ---
        elements.sort(key=lambda e: (round(e["bbox"][0], 2), round(e["bbox"][1], 2)))

        # --- Save page data ---
        pages_data[f"page_{page_index + 1}"] = {
            "width": page_width,
            "height": page_height,
            "elements": elements
        }

    return pages_data

def assign_line_numbers(page : dict, y_tolerance=3)-> list[dict]:
    """
    Assigns line numbers to elements based on their vertical (Y) positions.
    """
    elements = page['elements']
    # Step 1: Sort elements by Y (top of bounding box)
    elements = sorted(elements, key=lambda e: e["bbox"][0])

    lines = []
    current_line = []
    current_y = None
    line_number = 0

    for elem in elements:
        y_top = elem["bbox"][0]

        if current_y is None or abs(y_top - current_y) <= y_tolerance:
            current_line.append(elem)
            current_y = y_top if current_y is None else (current_y + y_top) / 2
        else:
            for e in current_line:
                e["line_number"] = line_number
            lines.append(current_line)
            line_number += 1

            # Start new line
            current_line = [elem]
            current_y = y_top

    # Final line
    for e in current_line:
        e["line_number"] = line_number
    lines.append(current_line)

    return elements
