import pymupdf as fitz 
import os

# Extract raw text and save images from a PDF.
def extract_text_and_images(pdf_path, image_output_folder="uploads/images"):
    os.makedirs(image_output_folder, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    full_text = ""
    image_paths = []

    for page_num, page in enumerate(doc):
        # Extract text
        full_text += page.get_text()

        # Extract images
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_path = f"{image_output_folder}/page{page_num}_img{img_index}.png"
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            image_paths.append(img_path)

    return full_text, image_paths