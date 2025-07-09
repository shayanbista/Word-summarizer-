import fitz
from PIL import Image
import io
import os
import cv2
import numpy as np

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not available. Using PyMuPDF rendering only.")
    print("To install: pip install pdf2image && sudo apt-get install poppler-utils")


def image_entropy(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()
    logs = np.log2(hist + 1e-7)
    entropy = -1 * (hist * logs).sum()
    return entropy


def has_pie_sectors(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue_var = np.std(hsv[:, :, 0])
    sat_var = np.std(hsv[:, :, 1])
    return hue_var > 10 and sat_var > 10


def is_pie_chart_shape(cnt, chart_region):
    perimeter = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
    if len(approx) > 8:
        area = cv2.contourArea(cnt)
        if area == 0:
            return False
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        circle_area = np.pi * (radius ** 2)
        circularity = area / circle_area
        if 0.75 < circularity < 1.25:
            return has_pie_sectors(chart_region)
    return False


def detect_bars_in_chart_region(chart_region):
    gray = cv2.cvtColor(chart_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bars = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 80:
            x, y, w, h = cv2.boundingRect(cnt)
            if (h > w and h > 20) or (w > h and w > 20):
                bars.append((x, y, w, h))
    return bars

def detect_charts_from_page_image(page_image, page_num, output_dir, min_area=10000):
    page_cv = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(page_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_charts = []

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h

        if w < 60 or h < 60 or w > 0.9 * page_cv.shape[1]:
            continue

        chart_region = page_cv[y:y + h, x:x + w]
        entropy = image_entropy(chart_region)
        if entropy < 2.0:
            continue

        chart_type = None
        if is_pie_chart_shape(contour, chart_region):
            chart_type = "pie"
        elif 0.4 < aspect_ratio < 3.5:
            chart_type = "bar"
        else:
            continue

        # Detect bars only if bar chart
        bars = detect_bars_in_chart_region(chart_region) if chart_type == "bar" else []
        
        # Skip if bar chart has less than 2 bars (not valid)
        if chart_type == "bar" and len(bars) < 2:
            continue  

        # Now save image only if all validations passed
        chart_filename = f"page{page_num}_{chart_type}_chart_{i + 1}.png"
        chart_path = os.path.join(output_dir, chart_filename)
        cv2.imwrite(chart_path, chart_region)

        detected_charts.append({
            "chart_type": chart_type,
            "chart_path": chart_path,
            "coordinates": (x, y, w, h),
            "area": area,
            "entropy": round(entropy, 2),
            "detected_bars": bars
        })

    return detected_charts


def extract_pdf_content_and_detect_charts(
    pdf_path, save_images=True, image_output_dir="output_charts", use_pdf2image=True
):
    doc = fitz.open(pdf_path)
    results = []

    if save_images and not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    page_images = None
    if use_pdf2image and PDF2IMAGE_AVAILABLE:
        print("Converting PDF to images...")
        try:
            page_images = convert_from_path(pdf_path, dpi=300)
            print(f"Converted {len(page_images)} pages.")
        except Exception as e:
            print(f"Error in pdf2image conversion: {e}")
            use_pdf2image = False

    for page_num in range(len(doc)):
        print(f"\nProcessing page {page_num + 1}...")
        page_dict = {"page": page_num + 1, "detected_charts": []}

        if use_pdf2image and page_images and page_num < len(page_images):
            page_image = page_images[page_num]
        else:
            print(f"Using PyMuPDF rendering for page {page_num + 1}")
            try:
                mat = fitz.Matrix(2.0, 2.0)
                pix = doc[page_num].get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                page_image = Image.open(io.BytesIO(img_data))
            except Exception as e:
                print(f"Error rendering page {page_num + 1}: {e}")
                continue

        detected_charts = detect_charts_from_page_image(
            page_image, page_num + 1, image_output_dir
        )
        page_dict["detected_charts"] = detected_charts
        print(f"Detected {len(detected_charts)} charts.")
        results.append(page_dict)

    doc.close()
    return results


def analyze_results(results):
    print("\n" + "=" * 50)
    print("DETECTION RESULTS SUMMARY")
    print("=" * 50)

    total_charts = 0
    total_bars = 0

    for page in results:
        print(f"\nPage {page['page']}:")
        charts = page["detected_charts"]
        print(f"  Charts detected: {len(charts)}")
        total_charts += len(charts)

        for chart in charts:
            bar_count = len(chart["detected_bars"])
            print(f"    - {chart['chart_path']} ({chart['chart_type']}): {bar_count} bars")
            total_bars += bar_count

    print(f"\nTOTAL SUMMARY:")
    print(f"  Total charts detected: {total_charts}")
    print(f"  Total bars detected: {total_bars}")


# === Run the script ===

results = extract_pdf_content_and_detect_charts(
    "./pdf files/piechart.pdf",
    save_images=True,
    image_output_dir="output_charts",
    use_pdf2image=True
)

analyze_results(results)

print("\n" + "=" * 50)
print("DETAILED RESULTS")
print("=" * 50)
for page in results:
    print(f"\nPage {page['page']}:")
    for chart in page["detected_charts"]:
        print(f"  Chart: {chart['chart_path']}")
        print(f"    Type: {chart['chart_type']}")
        print(f"    Area: {chart['area']}")
        print(f"    Entropy: {chart['entropy']}")
        print(f"    Coords: {chart['coordinates']}")
        print(f"    Bars: {chart['detected_bars']}")
