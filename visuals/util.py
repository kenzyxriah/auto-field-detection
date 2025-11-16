import base64
import io


def encode_image(img_bytes: bytes):
    return base64.b64encode(img_bytes).decode("utf-8")


import fitz  # PyMuPDF
from PIL import Image


def pdf_page_to_pil(pdf_path, page_number=0, zoom=2.0):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)  # 0-based indexing

    # Render page to a pixmap (image)
    mat = fitz.Matrix(zoom, zoom)  # control resolution
    pix = page.get_pixmap(matrix=mat)

    # Convert to PIL Image
    mode = "RGB" if pix.alpha == 0 else "RGBA"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

    return img


def format_by_type(candidates: list[dict]) -> dict[str, list]:
    result = {}
    type_counts = {}

    for item in candidates:
        item_type = item.get("type")
        bbox = item.get("bbox")

        if not item_type or not bbox:
            continue  # skip if missing info

        # Count how many times this type has occurred
        count = type_counts.get(item_type, 0)
        key = item_type if count == 0 else f"{item_type}_{count}"

        result[key] = bbox
        type_counts[item_type] = count + 1  # increment count

    return result


from PIL import ImageDraw
import cv2, uuid, numpy as np


def visualize_pil2(unique_candidates: list[dict], file_path: str, page_num: int, pdf_width, pdf_height):

    all_box = format_by_type(unique_candidates)
    pil_img = pdf_page_to_pil(file_path, page_num)
    draw = ImageDraw.Draw(pil_img)
    img_width, img_height = pil_img.size

    # Scaling factors
    scale_x = img_width / pdf_width
    scale_y = img_height / pdf_height

    for field_type, box in all_box.items():
        # PDF coordinates: [y0, x0, y1, x1]
        y0_pdf, x0_pdf, y1_pdf, x1_pdf = box

        # Scale to image coordinates
        x0 = x0_pdf * scale_x
        y0 = y0_pdf * scale_y
        x1 = x1_pdf * scale_x
        y1 = y1_pdf * scale_y

        # Draw rectangle
        draw.rectangle([x0, y0, x1, y1], outline="green", width=3)

        # Draw text label
        text_y = y0 - 10 if y0 - 10 > 0 else y0 + 10
        draw.text((x0, text_y), field_type, fill="red")

    save_path = f"output_page_{page_num}_{str(uuid.uuid4())[:7]}.jpg"  #'output.jpg'
    image_array = np.array(pil_img)
    cv2.imwrite(save_path, image_array)


def visualize_pil2_sign(
    unique_candidates: list[dict], file_path: str, page_num: int, pdf_width, pdf_height, image_map: dict = None
):
    """
    Draws or pastes provided base64 images on detected bounding boxes.

    :param unique_candidates: list of {type, bbox, pageNumber, ...}
    :param file_path: path to input PDF
    :param page_num: page index (0-based)
    :param pdf_width, pdf_height: PDF page size
    :param image_map: dict mapping type -> base64 image string (optional)
    """
    image_map = image_map or {}  # default to empty
    all_box = format_by_type(unique_candidates)

    # Render the PDF page to an image
    pil_img = pdf_page_to_pil(file_path, page_num)
    draw = ImageDraw.Draw(pil_img)
    img_width, img_height = pil_img.size

    # Scaling factors
    scale_x = img_width / pdf_width
    scale_y = img_height / pdf_height

    for field_type, box in all_box.items():
        y0_pdf, x0_pdf, y1_pdf, x1_pdf = box
        x0 = x0_pdf * scale_x
        y0 = y0_pdf * scale_y
        x1 = x1_pdf * scale_x
        y1 = y1_pdf * scale_y

        # Bounding box dimensions
        box_width = x1 - x0
        box_height = y1 - y0

        base64_data = image_map.get(field_type)

        if base64_data:
            # --- Decode the base64 image ---
            try:
                header, encoded = base64_data.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                overlay_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

                # --- Resize overlay to fit bbox ---
                overlay_resized = overlay_img.resize((int(box_width), int(box_height)))

                # --- Paste image into PDF page image ---
                pil_img.paste(overlay_resized, (int(x0), int(y0)), overlay_resized)
            except Exception as e:
                print(f"⚠️ Failed to draw image for {field_type}: {e}")
                draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
                draw.text((x0, y0 - 10), field_type, fill="red")
        else:
            # Fallback: draw box if no image provided
            draw.rectangle([x0, y0, x1, y1], outline="green", width=3)
            draw.text((x0, y0 - 10), field_type, fill="red")

    # Save output
    save_path = f"output_page_{page_num}_{str(uuid.uuid4())[:7]}.jpg"
    pil_img.save(save_path)
    print(f"✅ Saved visualization to {save_path}")
