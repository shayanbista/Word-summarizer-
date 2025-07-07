import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os

# def extract_pdf_content(pdf_path, save_images=False, image_output_dir="extracted_images"):
#     """
#     Extracts text, embedded images, and vector drawings from PDF pages.
#     :param pdf_path: Path to PDF file.
#     :param save_images: If True, saves images to image_output_dir.
#     :param image_output_dir: Directory to save images if save_images=True.
#     :return: List of dicts with keys 'page', 'text', 'images', 'drawings'
#     """
#     doc = fitz.open(pdf_path)
#     results = []

#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         page_dict = {'page': page_num + 1}

#         print(page_dict)

#         # Extract text
#         page_dict['text'] = page.get_text()
#         results.append(page_dict)

#     doc.close()
#     return results

# def extract_images_from_pdf(pdf_path, output_folder="pdf_images"):
#     doc = fitz.open(pdf_path)
#     os.makedirs(output_folder, exist_ok=True)
    
#     for page_index in range(len(doc)):
#         page = doc.load_page(page_index)
#         images = page.get_images(full=True)
#         print(f"Page {page_index + 1} has {len(images)} image(s)")
        
#         for img_index, img in enumerate(images):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             image_ext = base_image["ext"]
#             image = Image.open(io.BytesIO(image_bytes))
            
#             image_path = os.path.join(output_folder, f"page{page_index+1}_img{img_index+1}.{image_ext}")
#             image.save(image_path)
#             print(f"Saved image: {image_path}")


import fitz  # PyMuPDF
import os
import io
from PIL import Image

def extract_images_from_pdf(pdf_path, output_folder="pdf_images"):
    """
    Extracts all images from a PDF file and saves them to the specified output folder.

    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str): Directory where extracted images will be saved.
    """
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)
    
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        images = page.get_images(full=True)
        print(f"Page {page_index + 1} has {len(images)} image(s)")
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            
            image_path = os.path.join(
                output_folder, f"page{page_index+1}_img{img_index+1}.{image_ext}"
            )
            image.save(image_path)
            print(f"Saved image: {image_path}")





def extract_pdf_content(pdf_path, save_images=False, image_output_dir="extracted_images"):
    """
    Extracts text, embedded images, and vector drawings from PDF pages.
    :param pdf_path: Path to PDF file.
    :param save_images: If True, saves images to image_output_dir.
    :param image_output_dir: Directory to save images if save_images=True.
    :return: List of dicts with keys 'page', 'text', 'images', 'drawings'
    """
    doc = fitz.open(pdf_path)
    results = []
    
    # Create image output directory if saving images
    if save_images and not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)
    
    extract_images_from_pdf(pdf_path)

    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_dict = {'page': page_num + 1}
        
        print(f"Processing page {page_num + 1}...")
        
        # Extract text
        page_dict['text'] = page.get_text()
        
        # Extract images
        image_list = page.get_images(full=True)
        
        
        try:
            # Get drawing commands from the page
            drawings = page.get_drawings()
            for drawing in drawings:
                drawing_info = {
                    'type': drawing.get('type', 'unknown'),
                    'rect': drawing.get('rect', None),
                    'items': len(drawing.get('items', []))
                }
                page_dict['drawings'].append(drawing_info)
        except Exception as e:
            print(f"  Error extracting drawings: {str(e)}")
        
        results.append(page_dict)
    
    doc.close()
    return results