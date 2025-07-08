def extract_pdf_content(pdf_path, save_images=False):
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

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_dict = {'page': page_num + 1}
        
        print(f"Processing page {page_num + 1}...")
        
        # Extract text
        page_dict['text'] = page.get_text() 
        images = page.get_images(full=True)
        print(f"Page {page_num + 1} has {len(images)} image(s)")
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            
            image_path = os.path.join(
                output_folder, f"page{page_num+1}_img{img_index+1}.{image_ext}"
            )
            image.save(image_path)
            print(f"Saved image: {image_path}")
        
        results.append(page_dict)
    
    doc.close()
    return results