import fitz
from PIL import Image
import io
import os
import cv2
import numpy as np
import pytesseract
import easyocr
import re

USE_EASYOCR = True
EASYOCR_READER = None


def initialize_ocr(use_easyocr=True):
    global USE_EASYOCR, EASYOCR_READER
    USE_EASYOCR = use_easyocr
    if use_easyocr:
        EASYOCR_READER = easyocr.Reader(["en"])


def detect_charts_in_image(image):
    if isinstance(image, Image.Image):
        img_array = np.array(image)
    else:
        img_array = image

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    chart_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 10000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.3 < aspect_ratio < 3.0 and w > 200 and h > 200:
                chart_regions.append((x, y, w, h))

    return chart_regions


def detect_bar_charts_simple(image):
    if isinstance(image, Image.Image):
        img_array = np.array(image)
    else:
        img_array = image

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    chart_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 10000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.3 < aspect_ratio < 5.0 and w > 100 and h > 100:
                chart_regions.append((x, y, w, h))

    return chart_regions


def extract_text_from_chart(image, region=None):
    global USE_EASYOCR, EASYOCR_READER

    if isinstance(image, Image.Image):
        img_array = np.array(image)
    else:
        img_array = image

    if region:
        x, y, w, h = region
        img_array = img_array[y : y + h, x : x + w]

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(thresh, 3)

    extracted_text = []
    if USE_EASYOCR and EASYOCR_READER:
        results = EASYOCR_READER.readtext(denoised)
        for bbox, text, confidence in results:
            if confidence > 0.5:
                extracted_text.append(
                    {"text": text.strip(), "bbox": bbox, "confidence": confidence}
                )
    else:
        data = pytesseract.image_to_data(denoised, output_type=pytesseract.Output.DICT)
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 30:
                text = data["text"][i].strip()
                if text:
                    extracted_text.append(
                        {
                            "text": text,
                            "bbox": (
                                data["left"][i],
                                data["top"][i],
                                data["width"][i],
                                data["height"][i],
                            ),
                            "confidence": data["conf"][i],
                        }
                    )

    return extracted_text


def classify_chart_text(text_data):
    classified = {
        "titles": [],
        "axis_labels": [],
        "values": [],
        "legends": [],
        "other": [],
    }

    for item in text_data:
        text = item["text"]
        if re.match(r"^[A-Z][a-zA-Z\s]+$", text) and len(text) > 10:
            classified["titles"].append(item)
        elif re.match(r"^\d+(\.\d+)?$", text) or re.match(r"^\d+%$", text):
            classified["values"].append(item)
        elif len(text) < 20 and not re.match(r"^\d+", text):
            classified["axis_labels"].append(item)
        else:
            classified["other"].append(item)

    return classified


def extract_chart_data_values(chart_data):
    values = []
    labels = []

    classified_text = chart_data["classified_text"]

    for item in classified_text["values"]:
        text = item["text"]
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        for num in numbers:
            values.append(float(num))

    for item in classified_text["axis_labels"]:
        labels.append(item["text"])

    return {
        "values": values,
        "labels": labels,
        "title": (
            classified_text["titles"][0]["text"] if classified_text["titles"] else None
        ),
    }


def extract_pdf_content(
    pdf_path,
    save_images=True,
    image_output_dir="output_charts",
    detect_charts=True,
    use_easyocr=True,
):
    initialize_ocr(use_easyocr)

    if save_images and not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_dict = {"page": page_num + 1, "text": page.get_text(), "charts": []}

        print(f"Processing page {page_num + 1}...")

        if detect_charts:
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            chart_regions = detect_charts_in_image(image)
            bar_regions = detect_bar_charts_simple(image)

            all_regions = chart_regions[:]
            for bar_region in bar_regions:
                if bar_region not in all_regions:
                    all_regions.append(bar_region)

            page_dict["chart_regions"] = all_regions

            for i, region in enumerate(all_regions):
                x, y, w, h = region
                chart_img = image.crop((x, y, x + w, y + h))

                chart_path = None
                if save_images:
                    chart_filename = f"page_{page_num + 1}_chart_{i + 1}.png"
                    chart_path = os.path.join(image_output_dir, chart_filename)
                    chart_img.save(chart_path)

                chart_text = extract_text_from_chart(chart_img)
                classified_text = classify_chart_text(chart_text)
                chart_values = extract_chart_data_values(
                    {"classified_text": classified_text}
                )

                chart_data = {
                    "region": region,
                    "image_path": chart_path,
                    "raw_text": chart_text,
                    "classified_text": classified_text,
                    "title": chart_values.get("title"),
                    "labels": chart_values.get("labels"),
                    "values": chart_values.get("values"),
                    "source_pdf": os.path.basename(pdf_path),
                }

                page_dict["charts"].append(chart_data)

        results.append(page_dict)

    doc.close()
    return results
