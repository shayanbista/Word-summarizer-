import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Tuple
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import pytesseract
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def classify_image_content(image: np.ndarray) -> str:
    """
    Classify if an image contains graphs, plots, or other visual elements
    """
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Detect lines (common in graphs/plots)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    # Detect contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Classification logic
    line_count = len(lines) if lines is not None else 0
    contour_count = len(contours)
    
    # Check for text density
    text_density = cv2.countNonZero(gray) / (gray.shape[0] * gray.shape[1])
    
    if line_count > 20 and contour_count > 10:
        return "graph_plot"
    elif line_count > 10 and text_density < 0.3:
        return "diagram"
    elif text_density > 0.7:
        return "text_heavy"
    else:
        return "general_image"

def extract_text_from_image(image: np.ndarray) -> str:
    """
    Extract text from images using OCR
    """
    try:
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image)
        text = pytesseract.image_to_string(pil_image)
        return text.strip()
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        return ""

def analyze_graph_elements(image: np.ndarray) -> Dict[str, Any]:
    """
    Analyze graph/plot elements for better indexing
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Detect axes (horizontal and vertical lines)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    
    horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
    
    # Color analysis for different data series
    colors = image.reshape(-1, 3)
    unique_colors = len(np.unique(colors.view(np.dtype((np.void, colors.dtype.itemsize*colors.shape[1])))))
    
    # Detect data points/markers
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=1, maxRadius=10)
    data_points = len(circles[0]) if circles is not None else 0
    
    return {
        "has_axes": cv2.countNonZero(horizontal_lines) > 0 and cv2.countNonZero(vertical_lines) > 0,
        "color_complexity": unique_colors,
        "data_points": data_points,
        "chart_type": "scatter" if data_points > 20 else "line" if data_points > 0 else "bar"
    }

def process_pdf_with_classification(file_path: str) -> Dict[str, Any]:
    """
    Enhanced PDF processing with content classification
    """
    global vectorstore, retriever, pdf_loaded
    
    # Initialize containers for different content types
    text_documents = []
    image_documents = []
    graph_documents = []
    table_documents = []
    
    # Load PDF with PyMuPDF for image extraction
    pdf_document = fitz.open(file_path)
    
    # Also load with PyPDFLoader for text extraction
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Process each page
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Extract text content
        text_content = pages[page_num].page_content
        
        # Extract images from page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Get image data
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)
            
            if pix.n - pix.alpha < 4:  # Skip if not RGB/RGBA
                # Convert to numpy array
                img_data = np.frombuffer(pix.tobytes(), dtype=np.uint8)
                img_array = img_data.reshape(pix.height, pix.width, pix.n)
                
                if pix.n == 4:  # RGBA
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                
                # Classify image content
                content_type = classify_image_content(img_array)
                
                # Extract text from image
                ocr_text = extract_text_from_image(img_array)
                
                # Create document based on content type
                if content_type == "graph_plot":
                    # Analyze graph elements
                    graph_analysis = analyze_graph_elements(img_array)
                    
                    # Convert image to base64 for storage
                    img_pil = Image.fromarray(img_array)
                    buffer = io.BytesIO()
                    img_pil.save(buffer, format='PNG')
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    graph_doc = Document(
                        page_content=f"Graph/Plot from page {page_num + 1}: {ocr_text}\n"
                                   f"Analysis: {graph_analysis}\n"
                                   f"Chart type: {graph_analysis['chart_type']}\n"
                                   f"Has axes: {graph_analysis['has_axes']}\n"
                                   f"Data points: {graph_analysis['data_points']}",
                        metadata={
                            "page": page_num + 1,
                            "content_type": "graph_plot",
                            "chart_type": graph_analysis['chart_type'],
                            "has_axes": graph_analysis['has_axes'],
                            "data_points": graph_analysis['data_points'],
                            "image_base64": img_base64,
                            "ocr_text": ocr_text
                        }
                    )
                    graph_documents.append(graph_doc)
                
                elif content_type in ["diagram", "general_image"]:
                    # Convert image to base64 for storage
                    img_pil = Image.fromarray(img_array)
                    buffer = io.BytesIO()
                    img_pil.save(buffer, format='PNG')
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    img_doc = Document(
                        page_content=f"Image from page {page_num + 1}: {ocr_text}\n"
                                   f"Content type: {content_type}",
                        metadata={
                            "page": page_num + 1,
                            "content_type": content_type,
                            "image_base64": img_base64,
                            "ocr_text": ocr_text
                        }
                    )
                    image_documents.append(img_doc)
                
                elif content_type == "text_heavy":
                    # Treat as text document with OCR content
                    text_doc = Document(
                        page_content=f"Text from image on page {page_num + 1}: {ocr_text}",
                        metadata={
                            "page": page_num + 1,
                            "content_type": "ocr_text",
                            "source": "image_ocr"
                        }
                    )
                    text_documents.append(text_doc)
            
            pix = None  # Free memory
        
        # Extract tables (simple table detection)
        tables = page.find_tables()
        for table_index, table in enumerate(tables):
            table_data = table.extract()
            table_text = "\n".join(["\t".join(row) for row in table_data])
            
            table_doc = Document(
                page_content=f"Table from page {page_num + 1}:\n{table_text}",
                metadata={
                    "page": page_num + 1,
                    "content_type": "table",
                    "table_index": table_index
                }
            )
            table_documents.append(table_doc)
        
        # Process main text content
        text_doc = Document(
            page_content=text_content,
            metadata={
                "page": page_num + 1,
                "content_type": "main_text"
            }
        )
        text_documents.append(text_doc)
    
    pdf_document.close()
    
    # Combine all documents
    all_documents = text_documents + image_documents + graph_documents + table_documents
    
    # Split text documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_documents = []
    for doc in all_documents:
        if doc.metadata.get("content_type") in ["main_text", "ocr_text"]:
            # Split text documents
            splits = text_splitter.split_documents([doc])
            split_documents.extend(splits)
        else:
            # Keep image/graph/table documents as whole
            split_documents.append(doc)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(split_documents, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximum marginal relevance for diverse results
        search_kwargs={"k": 10, "lambda_mult": 0.25}
    )
    
    pdf_loaded = True
    
    # Return statistics
    stats = {
        "total_documents": len(split_documents),
        "text_documents": len([d for d in split_documents if d.metadata.get("content_type") in ["main_text", "ocr_text"]]),
        "image_documents": len([d for d in split_documents if d.metadata.get("content_type") in ["diagram", "general_image"]]),
        "graph_documents": len([d for d in split_documents if d.metadata.get("content_type") == "graph_plot"]),
        "table_documents": len([d for d in split_documents if d.metadata.get("content_type") == "table"]),
        "vectorstore": vectorstore,
        "retriever": retriever
    }
    
    return stats

def query_with_content_type(query: str, content_types: List[str] = None) -> List[Document]:
    """
    Query the vector store with optional content type filtering
    """
    if not pdf_loaded:
        return []
    
    # Get initial results
    results = retriever.get_relevant_documents(query)
    
    # Filter by content type if specified
    if content_types:
        filtered_results = []
        for doc in results:
            if doc.metadata.get("content_type") in content_types:
                filtered_results.append(doc)
        return filtered_results
    
    return results

# Example usage function
def search_graphs_and_plots(query: str) -> List[Document]:
    """
    Search specifically for graphs and plots
    """
    return query_with_content_type(query, ["graph_plot"])

def search_images(query: str) -> List[Document]:
    """
    Search specifically for images and diagrams
    """
    return query_with_content_type(query, ["diagram", "general_image"])

def search_tables(query: str) -> List[Document]:
    """
    Search specifically for tables
    """
    return query_with_content_type(query, ["table"])