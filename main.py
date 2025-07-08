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
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pytesseract
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os
import openai
import getpass

from sentence_transformers import SentenceTransformer
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from vector_store import Store


from fileProcessor import extract_pdf_content


def embed_text(text_chunks):
    embeddings = model.encode(text_chunks, convert_to_tensor=True)
    return embeddings

# OpenAI API Key
openai.api_key = "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"

def main():
    """
    Main function showing how to use the enhanced PDF processor
    """
    print("Processing PDF...")
    file_path = "./pdf files/test.pdf"     
    try:
        # Initialize the splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        split_pages = []

        # Call the enhanced processing function
        stats = extract_pdf_content(file_path)

        # # Split text by page
        for page in stats:
            chunks = splitter.split_text(page['text'])
            for i, chunk in enumerate(chunks):
                    split_pages.append({
                    'page': page['page'],
                    'chunk_number': i + 1,
                    'text': chunk,
                })


        Store((split_pages))

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return
    

if __name__ == "__main__":
    main()
