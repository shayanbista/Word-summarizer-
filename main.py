# Required imports and setup
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pytesseract
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os

from fileProcessor




# Global variables (same as your original code)
vectorstore = None
retriever = None
pdf_loaded = False

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# [Include all the functions from the previous artifact here]

# MAIN USAGE EXAMPLES
def main():
    """
    Main function showing how to use the enhanced PDF processor
    """
    print("Processing PDF...")
    file_path = "./pdf files/1.pdf"  
    
    try:
        # Call the enhanced processing function

        print(os)
        print(file_path)
        # stats = process_pdf_with_classification(file_path)
        
        # # Print processing statistics
        # print(f"\n📊 Processing Complete!")
        # print(f"Total documents created: {stats['total_documents']}")
        # print(f"Text documents: {stats['text_documents']}")
        # print(f"Image documents: {stats['image_documents']}")
        # print(f"Graph/Plot documents: {stats['graph_documents']}")
        # print(f"Table documents: {stats['table_documents']}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return
    

    
if __name__ == "__main__":
    main()

